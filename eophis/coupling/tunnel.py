"""
This module is a wrapper for python OASIS API.
"""
# eophis modules
from ..utils import logs
from ..utils.worker import Paral
from ..utils.params import Freqs
from .grid import make_subdomains, make_segments, fill_boundary_halos
# external modules
import pyoasis
from pyoasis import OASIS
import numpy as np

__all__ = ['Tunnel']

class Tunnel:
    """
    This class gathers a set of OASIS objects created during an Eophis execution under a common entity.
    This allows to spread OASIS commands between different identified coupled geoscientific codes
    
    Attributes
    ----------
    label : string
        Tunnel name
    grids : dict
        Tunnel user-defined grids
    exchs : list
        Tunnel user-defined exchanges
    geo_aliases : dict
        Correspondence between Tunnel and namcouple fields names from geophysical side
    py_aliases : dict
        Correspondence between Tunnel and namcouple fields names from Python side
    local_grids : dict
        local grid dimensions for parallel execution
    _partitions : dict
        list of OASIS Partition objects
    _variables : dict
        list of OASIS Var objects to receive ('rcv') and to send ('snd')
    _static_used : dict
        status of static variables (exchanged or not)
        
    """
    def __init__(self, label, grids, exchs, geo_aliases, py_aliases):
        self.label = label
        self.grids = grids
        self.exchs = exchs
        self.geo_aliases = geo_aliases
        self.py_aliases = py_aliases
        self.local_grids = {}
        self._inpartitions = {}
        self._outpartitions = {}
        self._variables = { 'rcv': {}, 'snd': {} }
        self._static_used = {}
        self._var2grid = {}
        
        # print some infos
        logs.info(f'-------- Tunnel {label} registered --------')
        logs.info(f'  namcouple variable names')
        logs.info(f'    Earth side:')
        for var,oas_var in geo_aliases.items():
            logs.info(f'      - {var} -> {oas_var}')
        logs.info(f'    Models side:')
        for var,oas_var in py_aliases.items():
            logs.info(f'      - {var} -> {oas_var}')

    def _configure(self, comp):
        """ Orchestrates OASIS definition methods. """
        self._define_partitions(comp.localcomm.rank,comp.localcomm.size)
        self._define_variables()
    
    def _define_partitions(self,myrank,oursize):
        """
        Create OASIS Partition from attributes
        
        Parameters
        ----------
        myrank : int
            local process rank
        oursize : int
            local communicator size
            
        """
        for grd_lbl, grd_params in self.grids.items():
            # params
            (nlon, nlat), halos, _ = grd_params.values()
            
            # output grid (without halos) dimensions
            sub_lon, sub_lat = make_subdomains(nlon,nlat,oursize)
            isub = myrank % len(sub_lon) 
            jsub = myrank // len(sub_lon)
            global_offset = sum(sub_lat[0:jsub]) * nlon + sum( sub_lon[0:isub] )
            # --> OASIS Box
            self._outpartitions[grd_lbl] = pyoasis.BoxPartition(global_offset, sub_lon[isub], sub_lat[jsub], nlon)

            # input grid (with halos) dimensions
            offsets, sizes, shifts, full_dim = make_segments(nlon, nlat, halos, sub_lon, sub_lat, myrank)
            self.local_grids[grd_lbl] = ( sub_lon[isub] + 2*halos, sub_lat[jsub] + 2*halos, shifts, full_dim )
            # --> OASIS Orange
            self._inpartitions[grd_lbl] = pyoasis.OrangePartition(list(offsets), list(sizes), nlon*nlat)

    def _define_variables(self):
        """ Create OASIS Variable from attributes and initialise status of static variables """
        for ex in self.exchs:
            for varin in ex['in']:
                self._variables['rcv'][varin] = pyoasis.Var(self.py_aliases[varin], self._partitions[ex['grd']], OASIS.IN, bundle_size=ex['lvl'])
                if ex['freq'] == Freqs.STATIC:
                    self._static_used[varin] = False
            for varout in ex['out']:
                self._variables['snd'][varout] = pyoasis.Var(self.py_aliases[varout], self._partitions[ex['grd']], OASIS.OUT, bundle_size=ex['lvl'])
                if ex['freq'] == Freqs.STATIC:
                    self._static_used[varout] = False

    def arriving_list(self):
        """ Return list of non-static receiveable variables """
        return [ lbl for ex in self.exchs for lbl in ex['in'] if ex['freq'] > 0 ]
    
    def departure_list(self):
        """ Return list of non-static sendable variables """
        return [ lbl for ex in self.exchs for lbl in ex['out'] if ex['freq'] > 0 ]

    def send(self, var_label, values, date=86579):
        """
        Send variable value to geoscientific code if date does match frequency exchange, nothing otherwise
        
        Parameters
        ----------
        var_label : string
            variable name to send
        date : int
            current simulation time
        values : numpy.ndarray
            array to send via OASIS under var_label
            
        Raises
        ------
        eophis.warning()
            if try to send an already sent static variable, then skip
        eophis.abort()
            if values does not match sending format
            
        """
        var = self._variables['snd'][var_label]
 
        # check static status
        if var_label in self._static_used and not self._static_used[var_label]:
            logs.info(f'\n-!- Static sending of {var_label} through tunnel {self.label}')
            self._static_used[var_label] = True
            date = 0
        elif var_label in self._static_used and self._static_used[var_label]:
            logs.warning(f'Static sending of {var_label} through tunnel {self.label} already done, skipped')
            return
        
        if values is not None and (date % var.cpl_freqs[0] == 0):
            # check shape
            if len(values.shape) != 3:
                logs.abort('  Shape of sending array for {var_label} must be equal to 3')
            # exclude halos, check size
            halos = self.grids[ self._var2grid[var_label] ]['halos']
            values = values[ halos : values.shape[0]-halos , halos : values.shape[1]-halos , : ]
            if (values.shape[0] * values.shape[1], values.shape[2]) != (var._partition_local_size, var.bundle_size):
                logs.abort(f'  Size of sending array for {var_label} does not match partition')
            # send field
            snd_fld = pyoasis.asarray(values)
            var.put( date, snd_fld )

    def receive(self, var_label, date=86579):
        """
        Request a variable reception from geoscientific code
        
        Parameters
        ----------
        var_label : string
            variable name to receive
        date : int
            current simulation time
            
        Raises
        ------
        eophis.warning()
            if try to receive an already received static variable, then skip
            
        Returns
        -------
        rcv_fld : numpy.ndarray
            array sent by geoscientific code, None if date does not match frequency exchange
            
        """
        rcv_fld = None
        var = self._variables['rcv'][var_label]
        
        # check static status
        if var_label in self._static_used and not self._static_used[var_label]:
            logs.info(f'\n-!- Static receive of {var_label} through tunnel {self.label}')
            self._static_used[var_label] = True
            date = 0
        elif var_label in self._static_used and self._static_used[var_label]:
            logs.warning(f'Static receive of {var_label} through tunnel {self.label} already done, skipped')
            return
        
        if (date % var.cpl_freqs[0] == 0):
            # get grid infos, receive field
            (nlon, nlat), halos, bnd = self.grids[ self._var2grid[var_label] ].values()
            loclon, loclat, shifts, full_dim = self.local_grids[ self._var2grid[var_label] ]
            rcv_fld = pyoasis.asarray( np.zeros( (loclon-2*halos*full_dim[0], loclat-2*halos*full_dim[1], var.bundle_size) ) )
            var.get(date, rcv_fld)
            # rebuild grid
            rcv_fld = np.roll(rcv_fld,shifts[0],axis=0)
            rcv_fld = np.roll(rcv_fld,shifts[1],axis=1)
            # build boundary halos if necessary
            rcv_fld = fill_boundary_halos(rcv_fld, halos, shifts, full_dim, bnd)
            # ----- FOR DEBUGGING ----
            #rcv_fld = rcv_fld + (Paral.RANK+1)/10.
            #if var_label == 'sst':
            #    Paral.EOPHIS_COMM.Barrier()
            #    logs.info(f'{Paral.RANK} -rcv- {rcv_fld}',Paral.RANK)
            # ------
        return rcv_fld


def init_oasis(comp_name='eophis'):
    """
    Initialize OASIS environment
    
    Parameters
    ----------
    comp_name : string
        OASIS component name
        
    Returns
    -------
    comp : pyoasis.Component
        created OASIS component
        
    """
    return pyoasis.Component(comp_name, True, Paral.GLOBAL_COMM)

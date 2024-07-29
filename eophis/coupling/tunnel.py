"""
This module is a wrapper for python OASIS API.
"""
# eophis modules
from ..utils import logs
from ..utils.worker import Paral
from ..utils.params import Freqs
from ..domain import Grid
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
    domains : eophis.Grid
        registered Grid objects
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
        self.domains = {}
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
        logs.info(f'    -------- Configure Tunnel {label} --------')
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
        # create grids
        for grd_label, grd_info in grids.items():
            nx, ny = grd_info['npts']
            grd_type, fold = 'T', 'T' if 'folding' not in grd_info.keys() else grd_info['folding']
            self.domains[grd_label] = Grid( label=grd_label, nx=nx, ny=ny, bnd=grd_info['bnd'], grd=grd_type, fold=fold )

            # define subdomain
            self.domains[grd_label].make_local_subdomain(domid=myrank, nsub=oursize, halo_size=grd_info['halos'])
            
            # output grid (without halos) --> OASIS Box
            global_offset, size_x, size_y, nx = self.domains[grd_label].as_box_partition()
            self._outpartitions[grd_lbl] = pyoasis.BoxPartition(global_offset, size_x, size_y, nx)

            # input grid (with halos) --> OASIS Orange
            off_seg, siz_seg, ncells = self.domains[grd_label].as_orange_partition()
            self._inpartitions[grd_lbl] = pyoasis.OrangePartition(off_seg, siz_seg, ncells)

    def _define_variables(self):
        """ Create OASIS Variable from attributes and initialise status of static variables """
        for ex in self.exchs:
            for varin in ex['in']:
                self._var2grid[varin] = ex['grd']
                self._variables['rcv'][varin] = pyoasis.Var(self.py_aliases[varin], self._inpartitions[ex['grd']], OASIS.IN, bundle_size=ex['lvl'])
                if ex['freq'] == Freqs.STATIC:
                    self._static_used[varin] = False
            for varout in ex['out']:
                self._var2grid[varout] = ex['grd']
                self._variables['snd'][varout] = pyoasis.Var(self.py_aliases[varout], self._outpartitions[ex['grd']], OASIS.OUT, bundle_size=ex['lvl'])
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
        # variable and grid
        var = self._variables['snd'][var_label]
        grd = self.domains[self._var2grid[var_label]]
 
        # check static status
        if var_label in self._static_used and not self._static_used[var_label]:
            logs.info(f'\n-!- Static sending of {var_label} through tunnel {self.label}')
            self._static_used[var_label] = True
            date = 0
        elif var_label in self._static_used and self._static_used[var_label]:
            logs.warning(f'Static sending of {var_label} through tunnel {self.label} already done, skipped')
            return
        
        # format field and send
        if values is not None and (date % var.cpl_freqs[0] == 0):
            values = grd.format_sending_array(values,var_label)
            values = pyoasis.asarray(values)
            var.put(date,values)

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
        # variable and grid
        var = self._variables['rcv'][var_label]
        grd = self.domains[self._var2grid[var_label]]

        # check static status
        if var_label in self._static_used and not self._static_used[var_label]:
            logs.info(f'\n-!- Static receive of {var_label} through tunnel {self.label}')
            self._static_used[var_label] = True
            date = 0
        elif var_label in self._static_used and self._static_used[var_label]:
            logs.warning(f'Static receive of {var_label} through tunnel {self.label} already done, skipped')
            return
        
        # get field and rebuild
        if (date % var.cpl_freqs[0] == 0):
            rcv_fld = grd.generate_receiving_array(var.bundle_size)
            rcv_fld = pyoasis.asarray(rcv_fld)
            var.get(date,rcv_fld)
            rcv_fld = grd.rebuild(rcv_fld)
            return rcv_fld
        else:
            return None


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

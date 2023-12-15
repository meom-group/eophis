"""
tunnel.py - this module is a wrapper for python OASIS API
"""
# eophis modules
from ..utils import logs
from ..utils.paral import COMM
from ..utils.params import Freqs
# external modules
import pyoasis
from pyoasis import OASIS
import numpy as np

__all__ = ['Tunnel']

class Tunnel:
    """
    This class gathers a set of OASIS objects created during an Eophis execution under a common entity.
    This allows to spread OASIS commands between different identified coupled earth-systems.
    
    Attributes:
        label: Tunnel name
        grids: Tunnel user-defined grids
        exchs: Tunnel user-defined exchanges
        es_aliases: Correspondence between exchange variables and namcouple names from earth-system side
        im_aliases: Same from inference models side
        local_grids: sliced grids dimensions for parallel execution
        _partitions: list of OASIS Partition objects
        _variables: list of OASIS Var objects
        _static_used: status of static variables (exchanged or not)
    Methods:
        arriving_list: return non-static variable names that can be received
        departure_list: return non-static variable names that can be sent
        send: wrapp OASIS steps for sending
        receive: wrapp OASIS steps for reception
        _configure: orchestrates OASIS definition methods
        _define_partitions: create OASIS Partitions from grids
        _define_variables: create OASIS Vars from exchs and aliases
    """
    def __init__(self, label, grids, exchs, es_aliases, im_aliases):
        # public
        self.label = label
        self.grids = grids
        self.exchs = exchs
        self.es_aliases = es_aliases
        self.im_aliases = im_aliases
        self.local_grids = {}
        # private
        self._partitions = {}
        self._variables = { 'rcv': {}, 'snd': {} }
        self._static_used = {}

        # print some infos
        logs.info(f'-------- Tunnel {label} created --------')
        logs.info(f'  namcouple variable names')
        logs.info(f'    Earth side:')
        for var,oas_var in es_aliases.items():
            logs.info(f'      - {var} -> {oas_var}')
        logs.info(f'    Models side:')
        for var,oas_var in im_aliases.items():
            logs.info(f'      - {var} -> {oas_var}')

    def _configure(self, comp):
        self._define_partitions(comp.localcomm.rank,comp.localcomm.size)
        self._define_variables()
    
    def _define_partitions(self,rank,size):
        """
        Create OASIS Partition from attributes
        
        Args:
            rank (int): local process rank
            size (int): local process size
        """
        for grd_lbl, (nlon, nlat, _, _) in self.grids.items():
            local_size = int(nlon * nlat / size)
            offset = rank * local_size
        
            if rank == size - 1:
                local_size = nlon * nlat - offset

            self.local_grids[grd_lbl] = [ int(nlon/size**0.5 ),int(nlat/size**0.5) ] 
            self._partitions[grd_lbl] = pyoasis.ApplePartition(offset, local_size)

    def _define_variables(self):
        """ Create OASIS Variable from attributes and initialise status of static variables """
        for ex in self.exchs:
            for varin in ex['in']:
                self._variables['rcv'][varin] = pyoasis.Var(self.im_aliases[varin], self._partitions[ex['grd']], OASIS.IN, bundle_size=ex['lvl'])
                self._static_used[varin] = False if ex['freq'] == Freqs.STATIC
            for varout in ex['out']:
                self._variables['snd'][varout] = pyoasis.Var(self.im_aliases[varout], self._partitions[ex['grd']], OASIS.OUT, bundle_size=ex['lvl'])
                self._static_used[varout] = False if ex['freq'] == Freqs.STATIC

    def arriving_list(self):
        """ Return list of non-static receiveable variables """
        return list( ex['in'][0] for ex in self.exchs if ex['freq'] > 0 )
    
    def departure_list(self):
        """ Return list of non-static sendable variables """
        return list( ex['out'][0] for ex in self.exchs if ex['freq'] > 0 )

    def ready(self):
        """ Return True if every static variables have been exchanged """
        return all( done for done in self._static_used.values() )

    def send(self, var_label, values, date=0):
        """
        Send variable value to earth-system if date does match frequency exchange, nothing otherwise
        
        Args:
            var_label (str): variable name to send
            date (int): current simulation time
            values (numpy.ndarray): array to send via OASIS under var_label
        """
        # static treatment
        if var_label in self._static_used and not self._static_used[var_label]:
            logs.info(f'\n-!- Static sending of {var_label} through tunnel {self.label}')
            self._static_used[var_label] = True
        elif var_label in self._static_used and self._static_used[var_label]:
            logs.warning(f'Static sending of {var_label} through tunnel {self.label} already done, skipped')
            return
        
        if values is not None:
            snd_fld = pyoasis.asarray(values)
            var = self._variables['snd'][var_label]
            if len(snd_fld.shape) != 3:
                logs.abort('  Shape of sending array for {var_label} must be equal to 3')
            if (snd_fld.shape[0] * snd_fld.shape[1], snd_fld.shape[2]) != (var._partition_local_size, var.bundle_size):
                logs.abort('  Size of sending array for {var_label} does not match partition')
            var.put(date, snd_fld)

    def receive(self, var_label, date=0):
        """
        Request a variable reception from earth-system
        
        Args:
            var_label (str): variable name to receive
            date (int): current simulation time
        Returns:
            rcv_fld (numpy.ndarray): array sent by earth-system, None if date does not match frequency exchange
        """
        rcv_fld = None
        var = self._variables['rcv'][var_label]
        
        # static treatment
        if var_label in self._static_used and not self._static_used[var_label]:
            logs.info(f'\n-!- Static receive of {var_label} through tunnel {self.label}')
            self._static_used[var_label] = True
        elif var_label in self._static_used and self._static_used[var_label]:
            logs.warning(f'Static receive of {var_label} through tunnel {self.label} already done, skipped')
            return
        
        if (date % var.cpl_freqs[0]) == 0:
            loclon, loclat = [ self.local_grids[ex['grd']] for ex in self.exchs if var_label in ex['in'] ][0]
            rcv_fld = pyoasis.asarray( np.zeros( (loclon,loclat,var.bundle_size) ) )
            var.get(date, rcv_fld)
        return rcv_fld


def init_oasis(comp_name='eophis'):
    """
    Initialize OASIS environment
    
    Args:
        comp_name (str): OASIS component name
    Returns:
        comp(pyoasis.Component): created OASIS component
    """
    return pyoasis.Component(comp_name, True, COMM)

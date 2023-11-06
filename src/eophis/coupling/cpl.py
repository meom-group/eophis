# eophis modules
from ..utils import logs
from ..utils.params import COMM
# external modules
import pyoasis
from pyoasis import OASIS
import numpy as np

__all__ = ['Tunnel']

class Tunnel:
    """
    Wrapper for python OASIS API
    
    Public Attributes
        label: Tunnel name
        grids: Tunnel user-defined grids
        exchs: Tunnel user-defined transferts
        aliases: Rename rules between user-defined variables and namcouple auto-writing
        
    Private Attributes
        _partitions: list of OASIS Partition objects
        _variables: list of OASIS Var objects
        
    Public Methods
        arriving_list: return variable names that can be received
        departure_list: return variables names that can be sent
        send: wrapp OASIS steps for sending
        receive: wrapp OASIS steps for reception
        
    Private Methods
        _configure: orchestrates definition methods below
        _define_partitions: create OASIS partitions from grids
        _define_variables: create OASIS variables from exchs and aliases
    """
    def __init__(self, label, grids, exchs, aliases):
        logs.info(f'-------- Tunnel {label} created')
        self.label = label
        self.grids = grids
        self.exchs = exchs
        self.aliases = aliases
        # Private
        self._partitions = {}
        self._variables = { "rcv": {}, "snd": {} }

    def _configure(self, comp):
        self._define_partitions(comp.localcomm.rank,comp.localcomm.size)
        self._define_variables()
    
    def _define_partitions(self,comm_rank,comm_size):
        for grd_lbl, (nlon, nlat, _, _) in self.grids.items():
            local_size = int(nlon * nlat / comm_size)
            offset = comm_rank * local_size
        
            if comm_rank == comm_size - 1:
                local_size = nlon * nlat - offset
                
            self._partitions[grd_lbl] = pyoasis.ApplePartition(offset, local_size, name=grd_lbl)

    def _define_variables(self):
        for ex in self.exchs:
            for varin in ex['in']:
                self._variables["rcv"][varin] = pyoasis.Var(self.aliases[varin], self._partitions[ex['grd']], OASIS.IN, bundle_size=ex['lvl'])
            for varout in ex['out']:
                self._variables["snd"][varout] = pyoasis.Var(self.aliases[varout], self._partitions[ex['grd']], OASIS.OUT, bundle_size=ex['lvl'])
    
    def arriving_list(self):
        return list(self._variables['rcv'].keys())
    
    def departure_list(self):
        return list(self._variables['snd'].keys())
    
    def send(self, var_label, date, values):
        if values is not None:
            snd_fld = pyoasis.asarray(values)
            var = self._variables["snd"][var_label]
            if snd_fld.shape != (3,):
                logs.abort('  Shape of sending array for var {var_label} must be equal to 3')
            if (snd_fld.shape[0] * snd_fld.shape[1], snd_fld.shape[2]) != (var._partition_local_size, var.bundle_size):
                logs.abort('  Size of sending array for {var_label} does not match partition')
            var.put(date, snd_fld)

    def receive(self, var_label, date):
        rcv_fld = None
        var = self._variables["rcv"][var_label]
        if (var.cpl_freqs() % date) == 0.0:
            rcv_fld = pyoasis.asarray(np.zeros((var._partition_local_size, var.bundle_size)))
            var.get(date, rcv_fld)
        return rcv_fld


def init_oasis(comp_name='eophis'):
    return pyoasis.Component(comp_name, True, COMM)

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
        es_aliases: Correspondence between exchange variables and namcouple names from earth-system side
        im_aliases: Same from inference models side
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
        for grd_lbl, (nlon, nlat, _, _) in self.grids.items():
            local_size = int(nlon * nlat / size)
            offset = rank * local_size
        
            if rank == size - 1:
                local_size = nlon * nlat - offset

            self.local_grids[grd_lbl] = [ int(nlon/size**0.5 ),int(nlat/size**0.5) ] 
            self._partitions[grd_lbl] = pyoasis.ApplePartition(offset, local_size)

    def _define_variables(self):
        for ex in self.exchs:
            for varin in ex['in']:
                self._variables['rcv'][varin] = pyoasis.Var(self.im_aliases[varin], self._partitions[ex['grd']], OASIS.IN, bundle_size=ex['lvl'])
            for varout in ex['out']:
                self._variables['snd'][varout] = pyoasis.Var(self.im_aliases[varout], self._partitions[ex['grd']], OASIS.OUT, bundle_size=ex['lvl'])
    
    def arriving_list(self):
        return list(self._variables['rcv'].keys())
    
    def departure_list(self):
        return list(self._variables['snd'].keys())
    
    def send(self, var_label, date, values):
        if values is not None:
            snd_fld = pyoasis.asarray(values)
            var = self._variables['snd'][var_label]
            if len(snd_fld.shape) != 3:
                logs.abort('  Shape of sending array for var {var_label} must be equal to 3')
            if (snd_fld.shape[0] * snd_fld.shape[1], snd_fld.shape[2]) != (var._partition_local_size, var.bundle_size):
                logs.abort('  Size of sending array for {var_label} does not match partition')
            var.put(date, snd_fld)

    def receive(self, var_label, date):
        rcv_fld = None
        var = self._variables['rcv'][var_label]
        if (date % var.cpl_freqs[0]) == 0.0:
            loclon, loclat = [ self.local_grids[ex['grd']] for ex in self.exchs if var_label in ex['in'] ][0]
            rcv_fld = pyoasis.asarray( np.zeros( (loclon,loclat,var.bundle_size) ) )
            var.get(date, rcv_fld)
        return rcv_fld


def init_oasis(comp_name='eophis'):
    return pyoasis.Component(comp_name, True, COMM)

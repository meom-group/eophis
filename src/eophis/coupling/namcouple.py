"""
namcouple.py - contains tools to create and manipulate OASIS namelist sections in right format
"""
# eophis modules
from .namelist import raw_content, find, replace, find_and_replace, write
from .tunnel import init_oasis, Tunnel
from ..utils.params import RANK, COMM
from ..utils import logs

__all__ = ['init_namcouple','register_tunnels','write_coupling_namelist','open_tunnels','close_tunnels']

class Namcouple:
    """
    This class represents the OASIS namelist 'namcouple' that is the most fundamental entity to setup couplings. Only one OASIS namelist is required for all couplings.
    The class provides tools for creation, manipulation and writing of namcouple file content. Every action related to Tunnel configuration is supervised by Namcouple.
    Modification of Namcouple without good understanding of OASIS libraries may lead to errors hard to track.
    
    For all these reasons, object Namcouple is a protected singleton that can only be handled from its API defined in same module.

    Attributes:
        infile/ (str): name of input/output namcouple file
        tunnels (eophis.Tunnel): registered Tunnel objects
        comp (pyoasis.Comp): main OASIS Component
        _lines (list) : namcouple file content
        _Nin (int): number of reception sections
        _Nout (int): number of sending sections
        _activated (bool): indicates if coupling environment is set
    Methods:
        _reset: unset coupling environment, reinit namcouple content
        _add_tunnel: update namcouple file content, create new Tunnel from updates
        _finalize: final namcouple updates, write file
        _activate: set OASIS environment, configure Tunnels
    """
    _instance = None
    
    def __new__(cls,*args,**kwargs):
        if not cls._instance:
            cls._instance = super(Namcouple, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self,file_path='',outfile=''):
        if not self.initialized:
            self.initialized = True
            self.infile = file_path
            self.outfile = outfile
            self.tunnels = []
            self.comp = None
            self._Nin = 0
            self._Nout = 0
            self._lines = raw_content(file_path)
            self._activated = False

    def _reset(self):
        del self.comp
        self.initialized = False
        self.__init__(self.infile,self.outfile)

    def _add_tunnel(self,label,grids,exchs,es_aliases={},im_aliases={}):
        logs.abort('OASIS environment set, impossible to create new tunnels') if self._activated else None
            
        replace(self._lines, '# ======= Tunnel '+label+' =======', len(self._lines)-2)
        for ex in exchs:
            for varin in ex['in']:
                im_aliases.update({ varin : 'M_IN_'+str(self._Nin) }) if varin not in im_aliases.keys() else None
                es_aliases.update({ varin : 'E_OUT_'+str(self._Nin) }) if varin not in es_aliases.keys() else None
                self._lines.insert( len(self._lines)-1, '# Earth -- '+varin+' --> Models')
                self._lines.insert( len(self._lines)-1, _create_bloc(es_aliases[varin],im_aliases[varin],ex['freq'],ex['grd'],*grids[ex['grd']]))
                self._Nin += 1
            for varout in ex['out']:
                im_aliases.update({ varout : 'M_OUT_'+str(self._Nout) }) if varout not in im_aliases.keys() else None
                es_aliases.update({ varout : 'E_IN_'+str(self._Nout) }) if varout not in es_aliases.keys() else None
                self._lines.insert( len(self._lines)-1, '# Earth <-- '+varout+' -- Models')
                self._lines.insert( len(self._lines)-1, _create_bloc(im_aliases[varout],es_aliases[varout],ex['freq'],ex['grd'],*grids[ex['grd']]))
                self._Nout += 1
        self._lines.insert(len(self._lines)-1, '#')
        
        self.tunnels.append( Tunnel(label,grids,exchs,es_aliases,im_aliases) )
        return self.tunnels[-1:][0]
    
    def _finalize(self,total_time):
        logs.abort('OASIS environment set, impossible to write namcouple') if self._activated else None
    
        # Update Nbfield and Runtime
        nfield = int(self._lines[ find(self._lines,'$NFIELDS') + 1 ]) + self._Nin + self._Nout
        runtime = int(self._lines[ find(self._lines,'$RUNTIME') + 1 ])
        find_and_replace(self._lines,'$NFIELDS',str(nfield),offset=1)
        if total_time > runtime:
            find_and_replace(self._lines,'$RUNTIME',str(total_time),offset=1)

        # Write namcouple
        write(self._lines,self.outfile,add_header=True) if RANK == 0 else None
        COMM.Barrier()

    def _activate(self):
        logs.abort('OASIS environment already set') if self._activated else None
    
        # Init all OASIS commands in tunnels
        self.comp = init_oasis()
        for tnl in self.tunnels:
            tnl._configure(self.comp)

        # Finalize OASIS coupling
        self.comp.enddef()
        self._activated = True



def _create_bloc(name_snd,name_rcv,freq,grd,nlon,nlat,overlap_x,overlap_y):
    """ Assemble infos to create a complete namcouple section """
    if overlap_x == 0 and overlap_y == 0:
        bnd = 'R 0 R 0'
    else:
        bnd = 'P '+str(abs(overlap_x))+' P '+str(abs(overlap_y))
    bloc = name_snd+' '+name_rcv+' 1 '+str(int(freq))+' 0 rst.nc EXPORTED\n'+ \
           str(nlon)+' '+str(nlat)+' '+str(nlon)+' '+str(nlat)+' '+str(grd)+' '+ \
           str(grd)+' LAG=0\n'+bnd
    return bloc



def init_namcouple(cpl_nml_tmp,cpl_nml):
    """
    read and init namcouple file
    
    Args:
        cpl_nml_tmp (str): input namcouple file
        cpl_nml (str): output namcouple file name
    """
    if Namcouple._instance is not None:
        logs.abort('Namcouple is not supposed to be instantiated before initialization routines')
    Namcouple(cpl_nml_tmp,cpl_nml)


def register_tunnels(*configs):
    """
    Namcouple API: update namcouple content and init Tunnel
    
    Args:
        config (dict): input metadata to create Tunnel
    Returns:
        List of created Tunnel objects
    """
    return [ Namcouple()._add_tunnel(**cfg) for cfg in configs ]


def write_coupling_namelist(simulation_time=31536000.0):
    """ Namcouple API: write namcouple at its current state """
    Namcouple()._finalize( int(simulation_time + simulation_time*1.01) )


def open_tunnels():
    """ Namcouple API: start coupling environment, create OASIS objects in Tunnels """
    Namcouple()._activate()


def close_tunnels():
    """ Namcouple API: terminate coupling environement """
    Namcouple()._reset()

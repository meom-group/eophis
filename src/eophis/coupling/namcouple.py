# eophis modules
from .namelists import raw_content, find, replace, find_and_replace, write
from .cpl import init_oasis, Tunnel
from ..utils.params import RANK, COMM
from ..utils import logs

__all__ = ['init_namcouple','register_tunnels','write_oasis_namelist','open_tunnels','close_tunnels']

class Namcouple:
    _instance = None
    """
    Tools to create OASIS namcouple sections in right format
    Namcouple is a singleton since only one OASIS namelist is required for all couplings
    
    Public attributes
        outfile: name of ouput namcouple file
        tunnels: registered tunnels
        comp: main OASIS component
    Private attributes
        _lines : raw namcouple file content
        _Nin: number of reception sections
        _Nout: number of sending sections
        _activated: indicates if coupling environment is set
    Private Methods
        -reset: unset coupling environment, reinit attributes
        _add_tunnel: create new Tunnel, update namcouple file content
        _finalize: final namcouple updates, write file
        _activate: set OASIS environment, configure Tunnels
    """
    def __new__(cls,*args,**kwargs):
        if not cls._instance:
            cls._instance = super(Namcouple, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self,file_path='',outfile=''):
        if not self.initialized:
            self.outfile = outfile
            self.tunnels = []
            self.comp = None
            self._Nin = 0
            self._Nout = 0
            self._lines = raw_content(file_path)
            self._activated = False
            self.initialized = True

    def _reset(self):
        del self.comp
        self.initialized = False
        self.__init__()
        self.initialized = False

    def _add_tunnel(self,label,grids,exchs):
        if self._activated:
            logs.abort('Oasis environment set, impossible to create new tunnels')
    
        aliases = {}
        replace(self._lines, "# ======= Tunnel "+label+" =======", len(self._lines)-2)
        for ex in exchs:
            for varin in ex['in']:
                aliases.update({ varin : "M_IN_"+str(self._Nin) })
                self._lines.insert( len(self._lines)-1, "# Earth -- "+varin+" --> Models")
                self._lines.insert( len(self._lines)-1, _create_bloc("E_OUT_"+str(self._Nin),aliases[varin],ex['freq'],ex['grd'],*grids[ex['grd']]))
                self._Nin += 1
            for varout in ex['out']:
                aliases.update({ varout : "M_OUT_"+str(self._Nout) })
                self._lines.insert( len(self._lines)-1, "# Earth <-- "+varout+" -- Models")
                self._lines.insert( len(self._lines)-1, _create_bloc(aliases[varout],"E_IN_"+str(self._Nout),ex['freq'],ex['grd'],*grids[ex['grd']]))
                self._Nout += 1
        self._lines.insert(len(self._lines)-1, "#")

        self.tunnels.append( Tunnel(label,grids,exchs,aliases) )
        return self.tunnels[-1:][0]
    
    def _finalize(self,total_time):
        if self._activated:
            logs.abort('Oasis environment set, impossible to write namcouple')
    
        # Update Nbfield and Runtime
        nfield = int(self._lines[ find(self._lines,'$NFIELDS') + 1 ]) + self._Nin + self._Nout
        find_and_replace(self._lines,'$NFIELDS',str(nfield),offset=1)
        find_and_replace(self._lines,'$RUNTIME',str(total_time),offset=1)

        # Write namcouple
        write(self._lines,self.outfile,add_header=True) if RANK == 0 else None
        COMM.Barrier()

    def _activate(self):
        if self._activated:
            logs.abort('Oasis environment already set')
    
        # Init all Oasis commands, spread them over tunnels
        self.comp = init_oasis()
        for tnl in self.tunnels:
            tnl._configure(self.comp)

        # Finalize OASIS coupling
        self.comp.enddef()
        self._activated = True


def _create_bloc(name_snd,name_rcv,freq,grd,nlon,nlat,overlap_x,overlap_y):
    if overlap_x == 0 and overlap_y == 0:
        bnd = "R 0 R 0"
    else:
        bnd = "P "+str(abs(overlap_x))+" P "+str(abs(overlap_y))
    bloc = name_snd+" "+name_rcv+" 1 "+str(int(freq))+" 0 rst.nc EXPOUT\n"+ \
           str(nlon)+" "+str(nlat)+" "+str(nlon)+" "+str(nlat)+" "+str(grd)+" "+ \
           str(grd)+" LAG=0\n"+bnd
    return bloc


"""
Public Namcouple API
    init_namcouple: explicit by itself
    register_tunnels: explicit by itself
    write_tunnel_namelist: write namcouple
    open_tunnels: start couling environement
    close_tunnels: terminate coupling environement
"""
def init_namcouple(cpl_nml_tmp,cpl_nml):
    if Namcouple._instance is not None:
        logs.abort('Namcouple is not supposed to be instantiated before initialization routines')
    Namcouple(cpl_nml_tmp,cpl_nml)

def register_tunnels(*configs):
    return [ Namcouple()._add_tunnel(**cfg) for cfg in configs ]

def write_oasis_namelist(simulation_time=31536000.0):
    Namcouple()._finalize( int(opening_time + opening_time*1.01) )

def open_tunnels():
    Namcouple()._activate()

def close_tunnels():
    Namcouple()._reset()

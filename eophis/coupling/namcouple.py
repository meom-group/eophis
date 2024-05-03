"""
Contains tools to create and manipulate OASIS namelist sections in right format.
"""
# eophis modules
from .namelist import raw_content, find, replace_line, find_and_replace_line, find_and_replace_char, write
from .tunnel import init_oasis, Tunnel
from ..utils.worker import Paral, set_local_communicator
from ..utils.params import Mode
from ..utils import logs
# external module
import re

__all__ = ['init_namcouple','register_tunnels','write_coupling_namelist','open_tunnels','tunnels_ready','close_tunnels']

class Namcouple:
    """
    This class represents the OASIS namelist 'namcouple'. This is the most fundamental entity to setup couplings. Only one OASIS namelist is required for all couplings.
    The class provides tools for creation, manipulation and writing of namcouple file content. Every action related to Tunnel configuration is supervised by Namcouple.
    Modification of Namcouple without good understanding of OASIS libraries may lead to errors hard to track.
    
    For all these reasons, object Namcouple is a protected singleton that can only be handled from its API defined in this module.

    Attributes
    ----------
        infile : string
            name of input namcouple file
        outfile : string
            name of output namcouple file
        tunnels : eophis.Tunnel)
            registered Tunnel objects
        comp : pyoasis.Comp
            main OASIS Component
        _lines : list( string )
            namcouple file content
        _reflines : list( string )
            unmodified namcouple file content
        _Nin : int
            number of reception sections
        _Nout : int
            number of sending sections
        _activated : bool)
            indicates if coupling environment is set
            
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
            self._read_namcouple()
            self._activated = False

    def _reset(self):
        """ unset coupling environment, reinit namcouple content. """
        del self.comp
        self.initialized = False
        self.__init__(self.infile,self.outfile)

    def _read_namcouple(self):
        """ read namcouple file from ``infile`` attribute, generate minimal content if empty. """
        self._lines = raw_content(self.infile)
        if len(self._lines) == 0:
            self._lines =  [ '$NFIELDS', '0', '$END', '############' ]
            self._lines += [ '$RUNTIME', '0', '$END', '############' ]
            self._lines += [ '$NLOGPRT', '1 0', '$END', '############' ]
            self._lines += [ '$STRINGS', '#', '$END' ]
        self._reflines = self._lines

    def _add_tunnel(self,label,grids,exchs,geo_aliases=None,py_aliases=None):
        """ update namcouple file content, create new Tunnel from updates. """
        # Default values
        geo_aliases = geo_aliases or {}
        py_aliases = py_aliases or {}
        
        # Skip if coupled
        if self._activated:
            logs.warning(f'Tunnels are opened, cannot register new tunnel {label}')
            return
            
        # content to add in namcouple, if production mode: check consistency
        replace_line(self._lines, '# ======= Tunnel '+label+' =======', len(self._lines)-2)
        for ex in exchs:
            for varin in ex['in']:
                py_aliases.update({ varin : 'M_IN_'+str(self._Nin) }) if varin not in py_aliases.keys() else None
                geo_aliases.update({ varin : 'E_OUT_'+str(self._Nin) }) if varin not in geo_aliases.keys() else None
                section = _make_and_check_section( geo_aliases[varin],py_aliases[varin],ex['freq'],ex['grd'],*grids[ex['grd']], nmcpl=self._reflines )
                self._lines.insert( len(self._lines)-1, '# Earth -- '+varin+' --> Models')
                self._lines.insert( len(self._lines)-1, section)
                self._Nin += 1
            for varout in ex['out']:
                py_aliases.update({ varout : 'M_OUT_'+str(self._Nout) }) if varout not in py_aliases.keys() else None
                geo_aliases.update({ varout : 'E_IN_'+str(self._Nout) }) if varout not in geo_aliases.keys() else None
                section = _make_and_check_section( py_aliases[varout],geo_aliases[varout],ex['freq'],ex['grd'],*grids[ex['grd']], nmcpl=self._reflines )
                self._lines.insert( len(self._lines)-1, '# Earth <-- '+varout+' -- Models')
                self._lines.insert( len(self._lines)-1, section)
                self._Nout += 1
        self._lines.insert(len(self._lines)-1, '#')

        self.tunnels.append( Tunnel(label,grids,exchs,geo_aliases,py_aliases) )
        return self.tunnels[-1:][0]
    
    def _finalize(self,total_time):
        """
        Final namcouple updates before writing, then write file.
        
        Parameters
        ----------
        total_time : int
            Simulation time to write in namcouple header section.
        
        """
        # Skip if coupled
        if self._activated:
            logs.warning('Tunnels are opened, cannot write coupling namelist')
            return
    
        # Update Nbfield and Runtime
        nfield = int(self._lines[ find(self._lines,'$NFIELDS') + 1 ]) + self._Nin + self._Nout
        runtime = int(self._lines[ find(self._lines,'$RUNTIME') + 1 ])
        find_and_replace_line(self._lines,'$NFIELDS',str(nfield),offset=1)
        if total_time > runtime:
            find_and_replace_line(self._lines,'$RUNTIME',str(total_time),offset=1)

        # Update static frequencies
        find_and_replace_char(self._lines,'-1',str(total_time))

        # Write namcouple
        write(self._lines,self.outfile,add_header=True) if Paral.RANK == Paral.MASTER else None
        Paral.EOPHIS_COMM.Barrier()

    def _activate(self):
        """ set OASIS environment, configure Tunnels. """
        # Skip if coupled
        if self._activated:
            logs.warning('Ignore tunnels opening, already done')
            return

        # set OASIS environment
        self.comp = init_oasis()
        set_local_communicator(self.comp.localcomm)
        logs.flush_buffer(Paral.MASTER)
        
        # init OASIS commands in tunnels
        for tnl in self.tunnels:
            tnl._configure(self.comp)

        # Finalize OASIS coupling
        self.comp.enddef()
        self._activated = True


def _make_and_check_section(name_snd,name_rcv,freq,grd,nlon,nlat,overlap_x,overlap_y,nmcpl=''):
    """
    Assemble tunnel infos to create a complete namcouple section.
    Check consistency with namcouple in production mode.
    
    Returns
    -------
    section : string
        section to write in OASIS namelist corresponding to given parameters
    
    Raises
    ------
    eophis.abort()
        if sections in read namcouple does not match sections required by registered tunnels, (production mode only)
    
    """
    section  = name_snd+' '+name_rcv+' 1 '+str(int(freq))+' 0 rst.nc EXPORTED\n'
    section += str(nlon)+' '+str(nlat)+' '+str(nlon)+' '+str(nlat)+' '+str(grd)+' '+ str(grd)+' LAG=0\n'
    section += 'R 0 R 0' if overlap_x == 0 and overlap_y == 0 else 'P ' + str(abs(overlap_x)) + ' P ' + str(abs(overlap_y))
           
    if Mode.PROD:
        # split section in fundamental subsections
        sct = section.split()
        secsize = len(''.join(sct))
        subsec = [ ''.join(sct[0:4]), '.nc'+''.join(sct[6]), ''.join(sct[7:13]), ''.join(sct[-4:]) ]
        
        # in case of static exchange...
        if freq == -1:
            total_time = nmcpl[ find(nmcpl,'$RUNTIME') +1 ]
            subsec[0] = subsec[0][:-2] + total_time
            secsize = secsize -2 + len(total_time)
        
        # find corresponding subsections in namcouple
        ref = re.sub(r'\s','',''.join(nmcpl))
        pos = ref.find(subsec[0])
        refsec = ref[ pos : pos + secsize ]
        # compare section and namcouple, stop if they do not match
        if not all ( sec in refsec for sec in subsec ):
            logs.abort(f'Section {" ".join(sct)} required by registered tunnel and namcouple do not match')
    return section


def init_namcouple(cpl_nml_tmp,cpl_nml):
    """
    Namcouple API: init and read namcouple file. Completely reinit Namcouple if it is already instantiated.
    

    Parameters
    ----------
    cpl_nml_tmp : string
        input namcouple file name
    cpl_nml : string
        output namcouple file name
        
    Raises
    ------
    eophis.warning()
        if Namcouple is already initialized

    Notes
    -----
    This function is automatically called when importing eophis package.

    """
    if Namcouple._instance is not None:
        logs.warning('Namcouple is already initialized and will be erased with a new instantiation')
        Namcouple._instance = None
        Namcouple(cpl_nml_tmp,cpl_nml)
    else:
        Namcouple(cpl_nml_tmp,cpl_nml)


def register_tunnels(configs):
    """
    Namcouple API: update namcouple content and init Tunnel
    
    Parameters
    ----------
    config : list
        list of input metadata to create Tunnels
        
    Returns
    -------
    tunnels : list( eophis.Tunnel )
        List of created Tunnel objects
        
    """
    return [ Namcouple()._add_tunnel(**cfg) for cfg in configs ]


def write_coupling_namelist(simulation_time=31536000.0):
    """
    Namcouple API: write namcouple at its current state
    
    Parameters
    ----------
    simulation_time : float
        Simulation time to write in namcouple header section
        
    Raises
    ------
    eophis.abort()
        if called in production mode
    
    """
    logs.info(f'\n  Writing namcouple with registered tunnels')
    logs.abort('OASIS namelist can only be written in preproduction mode') if not Mode.PREPROD else None
    Namcouple()._finalize( int( simulation_time*1.01) )


def open_tunnels():
    """
    Namcouple API: start coupling environment, create OASIS objects in Tunnels
        
    Raises
    ------
    eophis.abort()
        if called in preproduction mode
    
    """
    logs.info(f'\n  Starting coupling environment and tunnels opening')
    logs.abort('Tunnels opening can only be done in production mode') if not Mode.PROD else None
    Namcouple()._activate()


def tunnels_ready():
    """ Namcouple API: check if Tunnels are ready to start time loop. A Tunnel is ready if all the static exchanges have been done. """
    for tnl in Namcouple().tunnels:
        if not all( done for done in tnl._static_used.values() ):
            return False
    return True


def close_tunnels():
    """ Namcouple API: terminate coupling environement if set up. Reset Namcouple with same initialization attributes. """
    logs.info(f'\n  Closing tunnels')
    Namcouple()._reset()

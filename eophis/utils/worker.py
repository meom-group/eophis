"""
This module contains tools for parallel execution.
"""
# external modules
from mpi4py import MPI

__all__ = []

# global MPI infos
class Paral:
    """
    This class contains MPI variables commonly used in eophis.
    
    Attributes
    ----------
    GLOBAL_COMM : mpi4py.MPI.Intracomm
        Communicator of all coupled cpus
    GLOBAL_RANK : int
        Rank number of cpus in GLOBAL_COMM
    EOPHIS_COMM : mpi4py.MPI.Intracomm
        Communicator of eophis cpus
    RANK : int
        Rank numbering of cpus in EOPHIS_COMM
    MASTER : int
        Output rank
        
    """
    GLOBAL_COMM = MPI.COMM_WORLD
    GLOBAL_RANK = GLOBAL_COMM.Get_rank()
    EOPHIS_COMM = GLOBAL_COMM
    RANK = GLOBAL_RANK
    MASTER = 0


def set_local_communicator(new_comm):
    """
    Change eophis communicator and rank. This is useful when coupling environment is changing.
    
    Parameters
    ----------
    new_comm : mpi4py.MPI.Intracomm
        communicator with which all eophis processes will work
        
    """
    Paral.EOPHIS_COMM = new_comm
    Paral.RANK = Paral.EOPHIS_COMM.Get_rank()


def make_subdomain(nx,ny,nsub):
    """
    This function finds the best subdomain decomposition from global grid size and number of subdomains
    
    Parameters
    ----------
    nx,ny : int, int
        grid global size in x and y directions, respectively
    nsub : int
        number of subdomains
        
    Returns
    -------
    rankx : tuple( int )
        grid size for each subdomains in x direction
    ranky : tuple( int )
        grid size for each subdomains in y direction
        
    """
    target = max(nx/ny , ny/nx)
    diff0 = float('inf')
    
    # find integers px,py such as px*py = ncpu and px/py --> nx/ny
    for i in range(1, int(nsub**0.5) + 1):
        for j in range(i, nsub // i + 1):
            if i*j == nsub:
                diff = abs( j / i - target )
                if diff < diff0:
                    diff0 = diff
                    px = j if nx >= ny else i
                    py = i if nx >= ny else j
                    
    # decompose grid size over subdomains
    rankx = tuple( 1 + nx // px if i < nx % px else nx // px for i in range(px) )
    ranky = tuple( 1 + ny // py if i < ny % py else ny // py for i in range(py) )
    return rankx, ranky


def quit_eophis():
    """ Kill Eophis """
    Paral.GLOBAL_COMM.Abort(0)

"""
worker.py - This module contains tools for parallel execution
"""
# external modules
from mpi4py import MPI

__all__ = []

# global MPI infos
class Paral:
    """
    This class contains MPI variables commonly used in eophis
    
    Attributes:
        GLOBAL_COMM: Communicator of all coupled cpus
        GLOBAL_RANK: Rank number of cpus in GLOBAL_COMM
        EOPHIS_COMM: Communicator of eophis cpus
        RANK: Rank numbering of cpus in EOPHIS_COMM
        MASTER: Output rank
    Methods:
        set_local_communicator:
    """
    GLOBAL_COMM = MPI.COMM_WORLD
    GLOBAL_RANK = GLOBAL_COMM.Get_rank()
    EOPHIS_COMM = GLOBAL_COMM
    RANK = GLOBAL_RANK
    MASTER = 0


def set_local_communicator(new_comm):
    """ Change eophis communicator and rank with new_comm (mpi4py.MPI.Intracomm) """
    Paral.EOPHIS_COMM = new_comm
    Paral.RANK = Paral.EOPHIS_COMM.Get_rank()


def make_subdomain(nx,ny,ncpu):
    """
    This function finds the best subdomain decomposition from global grid size and number of cpus
    
    Args:
        nx,ny (int): grid global size in x and y directions, respectively
        ncpu (int): number of cpu
    Returns:
        rankx (tuple): grid size for each subdomains in x direction
        ranky (tuple): grid size for each subdomains in y direction
    """
    target = max(nx/ny , ny/nx)
    diff0 = float('inf')
    
    # find integers px,py such as px*py = ncpu and px/py --> nx/ny
    for i in range(1, int(ncpu**0.5) + 1):
        for j in range(i, ncpu // i + 1):
            if i*j == ncpu:
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

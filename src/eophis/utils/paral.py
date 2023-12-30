"""
paral.py - This module contains MPI variables commonly used in Eophis and tools for parallel decomposition
"""
# external modules
from mpi4py import MPI

# MPI tools
COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()
MASTER = 0


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
    MPI.Abort(COMM,0)

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


def quit_eophis():
    """ Kill Eophis """
    Paral.GLOBAL_COMM.Abort(0)

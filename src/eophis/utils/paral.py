"""
paral.py - This module contains: MPI variables commonly used in Eophis
"""

# external modules
from mpi4py import MPI

# MPI tools
COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()

def quit_eophis():
    MPI.Abort(COMM,0)

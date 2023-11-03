# external modules
from mpi4py import MPI

# MPI tools
COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()

# constants
class Freqs:
    HOURLY = 3600
    DAILY = 24 * HOURLY
    WEEKLY = 7 * DAILY
    MONTHLY = 31 * DAILY
    YEARLY = 365 * DAILY

class Grids:
    eORCA05 = [720,603,-2,-2]
    eORCA025 = [1440,1206,-2,-2]

# package export
from .coupling import *
from .loop import *
from .inference import *
from .utils import *

# eophis modules
from .utils import logs
from .coupling import _init_coupling
# external modules
from watermark import watermark
import atexit

"""
Eophis initialization
----------------------------
- print package infos
- call initialization routines
"""
def _init_eophis():
    logs.info('===============================')
    logs.info('     CNRS - IGE - MEOM Team    ')
    logs.info('            ------             ')
    logs.info('      EOPHIS 0.1.0 (2023)      ')
    logs.info('===============================')
    logs.info('Main packages used:')
    
    logs.info(watermark(packages="mpi4py,f90nml,numpy",python=True))
    
    # init coupling
    _init_coupling()
        
    # Schedule termination
    atexit.register(_finish_eophis)

def _finish_eophis():
    close_tunnels()
    logs.info('EOPHIS run successfully finished')


_init_eophis()

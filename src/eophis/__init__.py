# package export
from .coupling import *
from .loop import *
from .inference import *
from .utils import *

# eophis modules
from .utils import logs
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
    logs.info('     CNRS - IGE - MEOM Team    ')
    logs.info('===== EOPHIS 0.1.0 (2023) =====\n')
    logs.info('Main packages used:')
    
    logs.info(watermark(packages="mpi4py",python=True))
    logs.info(watermark(packages="f90nml",python=True))
    
    # init coupling
    _init_coupling()
        
    # Schedule termination
    atexit.register(_finish_eophis)

def _finish_eophis():
    # clean up
    close_tunnels()
    logs.info('EOPHIS run successfully finished')


_init_eophis()

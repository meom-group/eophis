"""
EOPHIS
======

Eophis is a collection of tools to deploy Python written scripts
for coupled execution with Fortran/C written physics-based models.

Available subpackages
---------------------
coupling
    tools to setup coupling environment
utils
    miscellaneous operating tools


* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
    
"""
# package export
from .coupling import *
from .domain import *
from .loop import *
from .utils import *

# eophis modules
from .utils import logs
from .utils.worker import Paral
from .coupling import _init_coupling
# external modules
from watermark import watermark
import pkg_resources as pkg
import atexit

def _init_eophis():
    """ Initializes Eophis: print package infos and call subpackage init routines. """
    ver = pkg.get_distribution("eophis").version
    logs.info(f'===============================')
    logs.info(f'|    CNRS - IGE - MEOM Team   |')
    logs.info(f'|           ------            |')
    logs.info(f'|     EOPHIS {ver} (2024)     |')
    logs.info(f'===============================')
    logs.info(f'Main packages used:')
    
    logs.info(watermark(packages="mpi4py,f90nml,numpy",python=True))
    
    # init coupling
    _init_coupling()
        
    # Schedule termination
    atexit.register(_finish_eophis)


def _finish_eophis():
    """ Executes cleaning processes at end of Eophis use. """
    close_tunnels()
    logs.info('\nEOPHIS run finished')
    logs.flush_buffer(Paral.MASTER)


_init_eophis()

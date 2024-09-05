"""
coupling subpackage
-------------------
This subpackage contains wrappers for:
    - OASIS component initialization and termination
    - partitions and variables definition
    - steps to perform data exchanges with coupled physical code
    - tools to create and manipulate OASIS and Fortran namelists
    
It also provides tools to read Fortran namelists and obtain informations about simulation executed by the physical code.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
    
"""
# package export
from .tunnel import *
from .namelist import *
from .namcouple import *

# eophis modules
from ..utils import logs
from ..utils.worker import Paral
# external modules
import os
import shutil

def _init_coupling():
    """
    Run the coupling subpackage initialization.
    
    Notes
    -----
    - Inquire coupling namelists 'namcouple' and 'namcouple_ref'
    - Create 'namcouple' from 'namcouple_ref' if exists, from scratch otherwise
    - Save copy of 'namcouple' as 'namcouple_ref' if exists alone
    - If both exist, does nothing and read 'namcouple'
    - instantiate Namcouple singleton with 'namcouple'
    
    """
    logs.info('---------------------------')
    logs.info('  Coupling Initialization  ')
    logs.info('---------------------------')
    logs.info('  Checking up OASIS namelists...')
    
    cpl_nml = os.path.join(os.getcwd(), 'namcouple')
    cpl_nml_ref = os.path.join(os.getcwd(), 'namcouple_ref')
   
    if not os.path.isfile(cpl_nml):
        logs.info(f'      namcouple not found, looking for reference file namcouple_ref')
        if not os.path.isfile(cpl_nml_ref):
            logs.info(f'      namcouple_ref not found either, creating it from scratch')
        else:
            logs.info(f'      namcouple_ref found, copied as namcouple')
            shutil.copy(cpl_nml_ref,cpl_nml)
    else:
        if not os.path.isfile(cpl_nml_ref):
            logs.info(f'      only namcouple found, save copy as {cpl_nml_ref}')
            shutil.copy(cpl_nml, cpl_nml_ref)
        else:
            logs.info(f'      namcouple and namcouple_ref found, nothing done')
            cpl_nml_ref = cpl_nml

    # Instantiate OASIS namcouple
    logs.info('  Reading namcouple\n')
    init_namcouple(cpl_nml_ref,cpl_nml)

# package import
from .cpl import *
from .namelists import *
from .namcouple import *

# eophis modules
from ..utils import logs, params
# external modules
import os
import shutil

"""
Coupling initialization
-----------------------
- Inquire namcouple file
- Copy namcouple file from Eophis reference if not
- Rename namcouple file to work with in peace (avoid other programs to start a coupling before namcouple automatic writing)
- instantiate Namcouple object
"""
def _init_coupling():
    logs.info('Coupling Initialization...')
    logs.info('  Looking for OASIS namelist "namcouple"')
    
    cpl_nml = os.path.join(os.getcwd(), "namcouple")
    cpl_nml_tmp = os.path.join(os.getcwd(), "namcouple_tmp")
    cpl_nml_ref = os.path.join(os.path.abspath(eophis.__file__)[:-18], "namcouple_ref")
    
    if params.RANK == 0:
        if not os.path.isfile(cpl_nml):
            shutil.copy(cpl_nml_ref, cpl_nml_tmp)
            logs.info('  "namcouple" not found, copy from {cpl_nml_ref} \n')
        else:
            os.rename(cpl_nml, cpl_nml_tmp)
            logs.info('  "namcouple" found\n')

    # Instantiate OASIS namcouple
    init_namcouple(cpl_nml_tmp,cpl_nml)

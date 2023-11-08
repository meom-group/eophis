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
- ...
- instantiate Namcouple object
"""
def _init_coupling():
    logs.info('---------------------------')
    logs.info('  Coupling Initialization  ')
    logs.info('---------------------------')
    logs.info('  Checking up OASIS namelists...')
    
    cpl_nml = os.path.join(os.getcwd(), 'namcouple')
    cpl_nml_ref = os.path.join(os.getcwd(), 'namcouple_ref')
    cpl_nml_base = os.path.join(os.path.abspath(cpl.__file__)[:-23], 'namcouple_eophis')
    
    if not os.path.isfile(cpl_nml):
        logs.info(f'    "namcouple" not found, looking for reference file "namcouple_ref"')
        if not os.path.isfile(cpl_nml_ref):
            logs.info(f'    "namcouple_ref" not found either, creating it from {cpl_nml_base} \n')
            shutil.copy(cpl_nml_base, cpl_nml_ref) if params.RANK == 0 else None
        else:
            logs.info(f'    "namcouple_ref" found, copied as "namcouple"\n')
            shutil.copy(cpl_nml_ref,cpl_nml) if params.RANK == 0 else None
    else:
        if not os.path.isfile(cpl_nml_ref):
            logs.info(f'    only "namcouple" found, save copy as {cpl_nml_ref}\n')
            shutil.copy(cpl_nml, cpl_nml_ref) if params.RANK == 0 else None
        else:
            logs.info(f'    "namcouple" and "namcouple_ref" found, nothing done\n')
            logs.warning(f'Priority given to "namcouple" for reading if "namcouple_ref" is also present')
            cpl_nml_ref = cpl_nml

    # Instantiate OASIS namcouple
    init_namcouple(cpl_nml_ref,cpl_nml)

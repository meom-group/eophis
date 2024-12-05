"""
This Eophis script creates material to couple toy_earth_tuto.py and models_tuto.py. OASIS interface is already hard-coded in toy_earth_tuto.py.

"""
import eophis
from eophis import Freqs
import os

def preproduction():
    """ Register Tunnel, write the coupling namelist from Tunnel registration and parameters in 'earth_namelist_tuto'. """
    eophis.info('========= EOPHIS TUTO : Pre-Production =========')
    eophis.info('  Aim: write coupling namelist\n')

    # 1. Define tunnel
    tunnel_config = list()
    tunnel_config.append( # ... )

    # 2. tunnel registration, compulsory to update namelist
    # ...

    # 3. get earth namelist
    earth_nml = # ...

    # get total simulation time from earth namelist
    step, it_end, it_0 = # ...
    total_time = # ...
    
    # 4. write namelist
    # ...

    
# ============================ #
if __name__=='__main__':

    # 5. set eophis mode
    eophis.set_mode( # ... )
    preproduction()

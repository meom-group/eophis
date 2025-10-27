"""
This Eophis script creates material to couple toy_earth_tuto.py and models_tuto.py. OASIS interface is already hard-coded in toy_earth_tuto.py.

"""
# eophis API
import eophis
from eophis import Freqs, Domains
# other modules
import argparse
import os

def toy_earth_info():
    """
    Return arguments for a Tunnel object that will configure coupling. Return an object from file 'earth_namelist' to manipulate its content.

    """

    # 1. Define tunnel
    tunnel_config = list()
    tunnel_config.append( # ... )

    # 2. get earth namelist
    earth_nml = # ...

    return tunnel_config, earth_nml


def preproduction():
    """ Register Tunnel, write the coupling namelist from Tunnel registration and parameters in 'earth_namelist_tuto'. """
    eophis.info('========= EOPHIS TUTO : Pre-Production =========')
    eophis.info('  Aim: write coupling namelist\n')

    # toy earth info
    tunnel_config, earth_nml = toy_earth_info()

    # 3. get total simulation time from earth namelist
    step, it_end, it_0 = # ...
    total_time = # ...

    # 4. tunnel registration (lazy) compulsory to update namelist
    eophis.register_tunnels( tunnel_config )

    # 5. write namelist
    # ...


def production():
    """
    Register and create Tunnel object (will compare coherence between Tunnel and namcouple content). Tunnel opening to starts coupling.
    Import Forcing Model from models_tuto.py
    Perform a static reception
    Assemble a Loop and a Router

    """
    eophis.info('========= EOPHIS TUTO : Production =========')
    eophis.info('  Aim: execute coupled simulation\n')

    #  toy Earth info
    tunnel_config, earth_nml = toy_earth_info()

    # simulation time from namelist
    step, it_end, it_0 = earth_nml.get('rn_Dt','nn_itend','nn_it000')
    niter = it_end - it_0 + 1
    total_time = niter * step

    # tunnel registration
    to_earth, = eophis.register_tunnels( tunnel_config )

    # 6. open tunels
    # ...

    # 7. static receive
    # ...

    # 8. Import Model
    # +++++++++++++++++
    # ...

    #  9. Assemble Loop and Router
    # +++++++++++++++++++++++++++++
    @eophis.all_in_all_out(   )
    def loop_core(**inputs):
        """
        Loop is defined with the decorator and time step informations from 'earth_namelist_tuto'.
        Content of loop_core is the Router. Connexions between exchanged variables and models are defined here.
        inputs dictionnary contains the variables that Eophis automatically received from toy_earth_tuto.py through OASIS.

        """
        outputs = {}
        outputs['an_output'] = a_model( inputs['an_input'] )
        return outputs

    #  Run
    # +++++
    eophis.starter(loop_core)

# ============================ #
if __name__=='__main__':
    """ Switch between preproduction and production mode. Call different instructions depending on the selected mode. """

    parser = argparse.ArgumentParser()
    parser.add_argument('--exec', dest='exec', type=str, default='prod', help='Execution type: preprod or prod')
    args = parser.parse_args()

    eophis.set_mode(args.exec)

    if args.exec == 'preprod':
        preproduction()
    elif args.exec == 'prod':
        production()
    else:
        eophis.abort(f'Unknown execution mode {args.exec}, use "preprod" or "prod"')

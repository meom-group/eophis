"""
This Eophis script manages coupling between fake_earth.py and models.py. OASIS interface is already hard-coded in fake_earth.py.
Purposes are to write coupling namelist during preproduction mode, configure OASIS interface for models.py, and orchestrate connexions between exchanged data and models.py.
Checkout docstrings in fake_earth.py and documentation to learn more about what coupling is supposed to achieve.

"""
# eophis API
import eophis
from eophis import Freqs, Domains
# other modules
import argparse
import os

def earth_info():
    """
    Return arguments for a Tunnel object that will configure coupling. Return an object from file 'earth_namelist' to manipulate its content.
    
    Two grids are associated with Tunnel TO_EARTH:
        1. 'demo' is a pre-defined grid of size (720,603) stored in Domains class, without halos
        2. 'lmdz' is a user-defined grid of size (180,151), without halos
    Three exchanges are defined in Tunnel TO_EARTH:
        1. receive first level of field sst, every simulated hours, on demo grid, and send back a variable sst_var with same properties
        2. receive 3 first levels of field svt, every simulated days, on demo grid, and send back a variable svt_var with same properties
        3. receive first level of field msk, only once, send back nothing
    
    Received fields sst and svt are filled by coupled script fake_earth.py. Work will be to define what values to return under sst_var and svt_var.
    This is done in loop_core().
    
    """
    tunnel_config = list()
    tunnel_config.append( { 'label' : 'TO_EARTH', \
                            'grids' : { 'demo' : Domains.demo, \
                                        'lmdz' :  {'npts' : (180,151)} }, \
                            'exchs' : [ {'freq' : Freqs.HOURLY, 'grd' : 'demo', 'lvl' : 1, 'in' : ['sst'], 'out' : ['sst_var'] },  \
                                        {'freq' : Freqs.DAILY,  'grd' : 'demo', 'lvl' : 3, 'in' : ['svt'], 'out' : ['svt_var'] },  \
                                        {'freq' : Freqs.STATIC, 'grd' : 'demo', 'lvl' : 1, 'in' : ['msk'], 'out' : [] } ] }
            # optional      'geo_aliases' : { 'sst' : 'EAR_SST', 'svt' : 'EAR_TEMP', 'sst_var' : 'EAR_SSTV', 'svt_var' : 'EARTEMPV'},  \
            # optional      'py_aliases'  : { 'sst' : 'EOP_SST', 'svt' : 'EOP_TEMP', 'sst_var' : 'EOP_SSTV', 'svt_var' : 'EOPTEMPV'}   }
                        )

    # earth namelist
    earth_nml = eophis.FortranNamelist(os.path.join(os.getcwd(),'earth_namelist'))
    return tunnel_config, earth_nml


def preproduction():
    """ Preproduction features: register Tunnel, write the coupling namelist from Tunnel registration and parameters in 'earth_namelist'. """
    eophis.info('========= EOPHIS DEMO : Pre-Production =========')
    eophis.info('  Aim: write coupling namelist\n')

    # earth info
    tunnel_config, earth_nml = earth_info()
    step, it_end, it_0 = earth_nml.get('rn_Dt','nn_itend','nn_it000')
    total_time = (it_end - it_0 + 1) * step

    # tunnel registration (lazy) compulsory to update namelist
    eophis.register_tunnels( tunnel_config )
    
    # write updated namelist
    eophis.write_coupling_namelist( simulation_time=total_time )


def production():
    """
    Production mode features: register and create Tunnel object (will compare coherence between Tunnel and namcouple content). Tunnel opening starts coupling.
    Import add_100() model from models.py
    Perform a static reception (msk)
    Assemble a Loop and a Router
    
    """
    eophis.info('========= EOPHIS DEMO : Production =========')
    eophis.info('  Aim: execute coupled simulation\n')

    #  Earth Coupling
    # ++++++++++++++++
    tunnel_config, earth_nml = earth_info()
    step, it_end, it_0 = earth_nml.get('rn_Dt','nn_itend','nn_it000')
    niter = it_end - it_0 + 1
    total_time = niter * step

    # tunnel registration (lazy)
    earth, = eophis.register_tunnels( tunnel_config )

    # link all tunnels (beware, dormant errors will likely appear here)
    eophis.open_tunnels()

    #  Models
    # ++++++++
    from models import add_100

    # static send/receive
    mask = earth.receive('msk')

    #  Assemble
    # ++++++++++
    @eophis.all_in_all_out(geo_model=earth, step=step, niter=niter)
    def loop_core(**inputs):
        """
        Loop is defined with the decorator and time step informations from 'earth_namelist'.
        Content of loop_core is the Router. Connexions between exchanged variables and models are defined here.
        inputs dictionnary contains the variables that Eophis automatically received from fake_earth.py through OASIS.
        sst_var is the result of add_100() with sst passed as argument, same with svt and svt_var.
        Fill 'outputs' dictionnary  will let Eophis knows what to send back to fake_earth.py through OASIS under corresponding key
        
        """
        outputs = {}
        outputs['sst_var'] = add_100(inputs['sst'])
        outputs['svt_var'] = add_100(inputs['svt']) 
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

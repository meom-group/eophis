"""
This Eophis script manages coupling between toy_earth_tuto.py and models_tuto.py. OASIS interface is already hard-coded in toy_earth_tuto.py.

"""
import eophis
from eophis import Freqs
import os

def production():
    """
    Register and create Tunnel object (will compare coherence between Tunnel and namcouple content). Tunnel opening to starts coupling.
    Import Forcing Model from models_tuto.py
    Perform a static reception
    Assemble a Loop and a Router
    
    """
    eophis.info('========= EOPHIS TUTO : Production =========')
    eophis.info('  Aim: execute coupled simulation\n')

    # Define tunnel
    tunnel_config = list()
    tunnel_config.append( { 'label' : 'TO_EARTH', \
                            'grids' : { 'grid_tuto' : {'npts' : (100,100)} }, \
                            'exchs' : [ {'freq' : 5, 'grd' : 'grid_tuto' , 'lvl' : 3, 'in' : ['U'], 'out' : ['force_U'] }, \
                                        {'freq' : Freqs.STATIC, 'grd' : 'grid_tuto' , 'lvl' : 1, 'in' : ['X'], 'out' : [] } ] }
                        )

    # tunnel registration
    to_earth, = eophis.register_tunnels( tunnel_config )

    # get earth namelist
    earth_nml = eophis.FortranNamelist(os.path.join(os.getcwd(),'earth_namelist_tuto'))

    # get total simulation time from earth namelist
    step, it_end, it_0 = earth_nml.get('rn_Dt','nn_itend','nn_it000')
    niter = it_end - it_0 + 1

    # 1. open tunnels
    # ...

    # 2. static receive
    # ...

    #  3. Import Model
    # +++++++++++++++++
    # ...

    #  4. Assemble Loop and Router
    # +++++++++++++++++++++++++++++
    @eophis.all_in_all_out( # ... )
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

    # 5. set eophis mode
    eophis.set_mode( # ... )
    production()

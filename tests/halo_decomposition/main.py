"""
This Eophis script manages coupling between toy_earth.py and models.py. OASIS interface is already hard-coded in toy_earth.py.
Purposes are to write coupling namelist during preproduction mode, configure OASIS interface for models.py, and orchestrate connexions between exchanged data and models.py.
Checkout docstrings in toy_earth.py and documentation to learn more about what coupling is supposed to achieve.

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
    
    Two grids are associated with Tunnel 'TO_EARTH' :
        1. grid_fold: global domain has cyclic east-west boundary condition, and NorthFold condition for north-south axis. (sub)grid will be built with 1 extra halo cell. NorthFold condition requires to specify grid type. Here, it represents V points of an Arakawa C-grid and folding is done around F point.
        2. grid_cycl: global domain has cyclic north-south boundary condition, and no specific condition for east-west axis. (sub)grid will be built with 2 extra halo cells.
    
    First exchange is done with fields defined on grid_fold, and manipulated with corresponding grid properties. Same on grid_cycl for second exchange.
    
    """
    # earth namelist
    earth_nml = eophis.FortranNamelist(os.path.join(os.getcwd(),'earth_namelist'))

    # coupling config
    tunnel_config = list()
    tunnel_config.append( { 'label' : 'TO_EARTH', \
                            'grids' : { 'grid_fold' : {'npts' : (10,10) , 'halos' : 1, 'bnd' : ('cyclic','NFold'), 'folding' : ('V','F') } , \
                                        'grid_cycl' : {'npts' : (10,10) , 'halos' : 2, 'bnd' : ('close','cyclic') } }, \
                            'exchs' : [ {'freq' : 2, 'grd' : 'grid_cycl' , 'lvl' : 3, 'in' : ['psi'], 'out' : ['dxpsi','dypsi'] } , \
                                        {'freq' : 2, 'grd' : 'grid_fold' , 'lvl' : 2, 'in' : ['phi'], 'out' : ['dxphi','dyphi'] }   ] }
                        )
    return tunnel_config, earth_nml


def preproduction():
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
    from models import deltaxy

    #  Assemble
    # ++++++++++
    @eophis.all_in_all_out(geo_model=earth, step=step, niter=niter)
    def loop_core(**inputs):
        outputs = {}
        outputs['dxpsi'], outputs['dypsi'] = deltaxy(inputs['psi'])
        outputs['dxphi'], outputs['dyphi'] = deltaxy(inputs['phi'])
        return outputs

    #  Run
    # +++++
    eophis.starter(loop_core)
    
# ============================ #
if __name__=='__main__':

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

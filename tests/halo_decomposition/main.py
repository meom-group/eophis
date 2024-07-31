# eophis API
import eophis
from eophis import Freqs, Domains
# other modules
import argparse
import os

def earth_info():
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
    from eophis.utils.worker import Paral

    #  Assemble
    # ++++++++++
    @eophis.all_in_all_out(geo_model=earth, step=step, niter=niter)
    def loop_core(**inputs):
        outputs = {}
        outputs['dxpsi'], outputs['dypsi'] = deltaxy(inputs['psi'], (Paral.RANK+1) / 10. )
        outputs['dxphi'], outputs['dyphi'] = deltaxy(inputs['phi'], (Paral.RANK+1) / 10. )
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

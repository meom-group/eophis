"""
Toy Earth (TE) script emulates a surrogate geoscientific code with an hard-coded OASIS interface.
Purpose of TE is to test Eophis behavior in real conditions, without deploying an entire heavy geoscientific model.
It is coupled with the Python code contained in models.py in which the coupling interface has been deployed by Eophis.
Coupling namelist is also written by Eophis

TE initializes the data and sends them first to the coupled model. Returned data may be compared to expected results.
Coupling, content of TE and models.py may be adapted in order to test different features.


HALO DECOMPOSITION
------------------
TE advances in time with parameters provided in "earth_namelist".
It intends to send two fields psi and phi, and to receive their first order discrete differences along first and second axis.
Differences are also computed in TE with complete grid and compared with returned results. Test fails if results do not match.

Differences imply to know neighboring cells. Those will be missing at boundaries, especially if Python model is scattered among processes.
Fields need to be received on the model side with at least 1 extra halo cell to compute correct differences. Halo cells should not be kept after.
It is also required to specify what values should contain the halos located at the boundaries of the global grid.

TE is supposed to send/receive real cells only, without halos.
This test case checks the capability of Eophis to achieve fields exchanges with correct automatic reconstruction and rejection of halos. It means that:
    - Eophis correctly created halos with right values: wrong returned differences if not
    - Eophis returned the grid without the halos: presence of boundary-miscomputed differences if not

First field phi sent by TE is defined on Arakawa C-grid V-points, with cyclic/NF conditions for east-west/north-south boundary conditions, respectively.
Folding is done around F point and field is rebuilt with 1 halo.
Second field psi sent by TE is defined on a grid with close/cyclic boundary conditions. Wihtout NF condition, grid type (T-point, U-point...) does not matter. It is rebuilt with 2 halos.

"""
# oasis modules
import pyoasis
from pyoasis import OASIS
from mpi4py import MPI
# utils modules
import f90nml as nml
import numpy as np
import logging
import time

# ================= 
#       Utils
# =================
def make_edge_phi( array ):
    """ Build halo cells for the entire phi grid. """
    # build north edge
    folded_halos = array[ :, 1:2 , : ].copy()
    folded_halos = np.flip( folded_halos , axis=(0,1) )
    folded_halos = np.roll( folded_halos , 0 , axis=0 )
    edged_array = np.hstack( (folded_halos,array) )
        
    # build south edge
    up = edged_array[:,:1,:].copy()
    up = up * 0.0
    edged_array = np.hstack( (edged_array,up)  )

    # build east-west edges
    left = edged_array[:1,:,:].copy()
    right = edged_array[-1:,:,:].copy()
    edged_array = np.vstack( (right,edged_array)  )
    edged_array = np.vstack( (edged_array,left) )
    return edged_array

def make_edge_psi( array ):
    """ Build halo cells for the entire psi grid. """
    # build north-south edges
    up = array[:,:1,:].copy()
    bottom = array[:,-1:,:].copy() 
    array = np.hstack( (bottom,array)  )
    array = np.hstack( (array,up) )

    # build east-west edges
    left = array[:1,:,:].copy() * 0.0
    right = array[-1:,:,:].copy() * 0.0
    array = np.vstack( (right,array)  )
    array = np.vstack( (array,left) )
    return array


# ================ 
#       Main
# ================
def main():
    # +++++++++++++++++++++++++
    #   OASIS: INITIALISATION
    # +++++++++++++++++++++++++
    comm = MPI.COMM_WORLD
    component_name = "toy_earth"
    comp = pyoasis.Component(component_name,True,comm)

    comm_rank = comp.localcomm.rank
    comm_size = comp.localcomm.size 
    
    if comm_rank == 0:
        logging.info('  -----------------------------------------------------------')
        logging.info('  Component name %s with ID: %.1i' % (component_name,comp._id))
        logging.info('  Running with %.1i processes' % comm_size)
        logging.info('  -----------------------------------------------------------')

    # ++++++++++++++++++++++++++
    #   OASIS: GRID DEFINITION
    # ++++++++++++++++++++++++++
    grd_src = 'torc'
    nlon = 10
    nlat = 10
    nlvl = 3

    if comm_rank == 0:
        logging.info('  Grid name: %s' % grd_src)
        logging.info('  Grid size: %.1i %.1i %.1i' % (nlon, nlat, nlvl))
        logging.info('  End Of Grid Def')

    # +++++++++++++++++++++++++++++++
    #   OASIS: PARTITION DEFINITION
    # +++++++++++++++++++++++++++++++
    local_size = int(nlon * nlat / comm_size)
    offset = comm_rank * local_size

    if comm_rank == comm_size - 1:
        local_size = nlon * nlat - offset

    partition = pyoasis.ApplePartition(offset,local_size)
    
    if comm_rank == 0:
        logging.info('  End Of Part Def')
        
    # +++++++++++++++++++++++++++++++
    #   OASIS: VARIABLES DEFINITION
    # +++++++++++++++++++++++++++++++
    var_out = ['E_OUT_0','E_OUT_1']
    var_in = ['E_IN_0','E_IN_1','E_IN_2','E_IN_3']

    dat_psi = pyoasis.Var(var_out[0],partition,OASIS.OUT,bundle_size=nlvl)
    dat_phi = pyoasis.Var(var_out[1],partition,OASIS.OUT,bundle_size=2)
    
    res_dxpsi = pyoasis.Var(var_in[0],partition,OASIS.IN,bundle_size=nlvl)
    res_dypsi = pyoasis.Var(var_in[1],partition,OASIS.IN,bundle_size=nlvl)
    res_dxphi = pyoasis.Var(var_in[2],partition,OASIS.IN,bundle_size=2)
    res_dyphi = pyoasis.Var(var_in[3],partition,OASIS.IN,bundle_size=2)

    if comm_rank == 0:
        logging.info('  End Of Var Def')

    # ++++++++++++++++++++++++++++
    #   OASIS: END OF DEFINITION
    # ++++++++++++++++++++++++++++
    comp.enddef()
    
    if comm_rank == 0:
        logging.info('  End Of Definition')
        
    # +++++++++++++++
    #   INIT ARRAYS
    # +++++++++++++++
    # Init entire psi/phi grid, isolate part corresponding to local process
    psi = np.arange(nlon*nlat*nlvl).reshape(nlon*nlat,nlvl,order='F')
    psi = psi[offset:offset+local_size,:]
    psi = pyoasis.asarray(psi)
    phi = np.arange(nlon*nlat*2).reshape(nlon*nlat,2,order='F')
    phi = phi[offset:offset+local_size,:]
    phi = pyoasis.asarray(phi)
    # Reception fields, initialized to zero
    dxpsi = pyoasis.asarray( np.zeros((local_size,nlvl)) )
    dypsi = pyoasis.asarray( np.zeros((local_size,nlvl)) )
    dxphi = pyoasis.asarray( np.zeros((local_size,2)) )
    dyphi = pyoasis.asarray( np.zeros((local_size,2)) )

    # +++++++++++++++++++++++++++
    #   TIME INFO FROM NAMELIST
    # +++++++++++++++++++++++++++
    namelist = nml.read('earth_namelist')
    
    time_step = int( namelist['namdom']['rn_Dt'] )
    niter = int( namelist['namrun']['nn_itend'] - namelist['namrun']['nn_it000'] ) + 1
    total_time = niter*time_step

    if comm_rank == 0:
        logging.info('  -----------------------------------------------------------')
        logging.info('  Number of iterations: %.1i' % niter)
        logging.info('  Time step: %.1i' % time_step)
        logging.info('  Simulation length: %.1i' % total_time)
        logging.info('  -----------------------------------------------------------')

    # +++++++++++++++++
    #   RUN EXCHANGES
    # +++++++++++++++++
    # Loop for time advancement
    for it in range(niter):
        it_sec = int(time_step * it)
        
        if comm_rank == 0:
            logging.info(f'  Ite {it}:')

        # send fields
        if it_sec%dat_psi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_psi._name))

        if it_sec%dat_phi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_phi._name))

        dat_psi.put(it_sec,psi)
        dat_phi.put(it_sec,phi)

        # receive fields
        if it_sec%res_dxpsi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (res_dxpsi._name))

        if it_sec%res_dypsi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (res_dypsi._name))

        if it_sec%res_dxphi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (res_dxphi._name))

        if it_sec%res_dyphi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (res_dyphi._name))

        res_dxpsi.get(it_sec,dxpsi)
        res_dypsi.get(it_sec,dypsi)
        res_dxphi.get(it_sec,dxphi)
        res_dyphi.get(it_sec,dyphi)

    if comm_rank == 0:
        logging.info('  End Of Loop')
  
    # ++++++++++++++++++
    #     REFERENCES
    # ++++++++++++++++++
    # create entire psi grid
    ref_psi = np.arange(nlon*nlat*nlvl).reshape(nlon,nlat,nlvl,order='F')
    # add halos on entire psi grid
    ref_psi = make_edge_psi(ref_psi)
    # compute differences
    ref_dxpsi = np.diff(ref_psi,axis=0,append=ref_psi[0:1,:,:])
    ref_dypsi = np.diff(ref_psi,axis=1,prepend=ref_psi[:,0:1,:])
    # remove halos
    ref_dxpsi = ref_dxpsi[1:-1,1:-1,:]
    ref_dypsi = ref_dypsi[1:-1,1:-1,:]
    # isolate part corresponding to local process
    ref_dxpsi = ref_dxpsi.reshape(nlon*nlat,nlvl,order='F')
    ref_dypsi = ref_dypsi.reshape(nlon*nlat,nlvl,order='F')
    ref_dxpsi = ref_dxpsi[offset:offset+local_size,:]
    ref_dypsi = ref_dypsi[offset:offset+local_size,:]
   
    # create entire phi grid
    ref_phi = np.arange(nlon*nlat*2).reshape(nlon,nlat,2,order='F')
    # add halos on entire phi grid
    ref_phi = make_edge_phi(ref_phi)
    # compute differences
    ref_dxphi = np.diff(ref_phi,axis=0,append=ref_phi[0:1,:,:])
    ref_dyphi = np.diff(ref_phi,axis=1,prepend=ref_phi[:,0:1,:])
    # remove halos
    ref_dxphi = ref_dxphi[1:-1,1:-1,:]
    ref_dyphi = ref_dyphi[1:-1,1:-1,:]
    # isolate part corresponding to local process
    ref_dxphi = ref_dxphi.reshape(nlon*nlat,2,order='F')
    ref_dyphi = ref_dyphi.reshape(nlon*nlat,2,order='F')
    ref_dxphi = ref_dxphi[offset:offset+local_size,:]
    ref_dyphi = ref_dyphi[offset:offset+local_size,:]

    # +++++++++++++++
    #   FINAL CHECK
    # +++++++++++++++
    check_1 = np.array_equal(ref_dxpsi,dxpsi)
    check_2 = np.array_equal(ref_dypsi,dypsi)
    check_3 = np.array_equal(ref_dxphi,dxphi)
    check_4 = np.array_equal(ref_dyphi,dyphi)
    if check_1 and check_2 and check_3 and check_4:
        if comm_rank == 0:
            logging.info('  TEST SUCCESSFUL')
            print('TEST SUCCESSFUL')
    else:
        if comm_rank == 0:
            logging.info('  TEST FAILED')
            print('TEST FAILED')
        quit()

    # +++++++++++++++++++++++++
    #        TERMINATION
    # +++++++++++++++++++++++++
    del comp

    if comm_rank == 0:
        logging.info('  End Of Earth Program')


if __name__=="__main__":
    logging.basicConfig(filename='earth.log',encoding='utf-8',level=logging.INFO)
    main()

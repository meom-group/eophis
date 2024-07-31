# oasis modules
import pyoasis
from pyoasis import OASIS
from mpi4py import MPI
# utils modules
import f90nml as nml
import numpy as np
import logging
import time

def make_edge_phi( array , fold=False ):
    # build north edge
    folded_halos = array[ :, 1:2 , : ].copy()
    folded_halos = np.flip( folded_halos )
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

def make_edge_psi( array , fold=False ):
    # build north-south edges
    up = array[:,:1,:].copy() * 0.0
    bottom = array[:,-1:,:].copy() * 0.0
    array = np.hstack( (bottom,array)  )
    array = np.hstack( (array,up) )

    # build east-west edges
    left = array[:1,:,:].copy()
    right = array[-1:,:,:].copy()
    array = np.vstack( (right,array)  )
    array = np.vstack( (array,left) )
    return array



def main():
    # ++++++++++++++++++
    #   INITIALISATION
    # ++++++++++++++++++
    comm = MPI.COMM_WORLD
    component_name = "fake_earth"
    comp = pyoasis.Component(component_name,True,comm)

    comm_rank = comp.localcomm.rank
    comm_size = comp.localcomm.size 
    
    if comm_rank == 0:
        logging.info('  -----------------------------------------------------------')
        logging.info('  Component name %s with ID: %.1i' % (component_name,comp._id))
        logging.info('  Running with %.1i processes' % comm_size)
        logging.info('  -----------------------------------------------------------')

    # +++++++++++++++++++
    #   GRID DEFINITION
    # +++++++++++++++++++
    grd_src = 'torc'
    nlon = 10
    nlat = 10
    nlvl = 3

    if comm_rank == 0:
        logging.info('  Grid name: %s' % grd_src)
        logging.info('  Grid size: %.1i %.1i %.1i' % (nlon, nlat, nlvl))
        logging.info('  End Of Grid Def')

    # ++++++++++++++++++++++++
    #   PARTITION DEFINITION
    # ++++++++++++++++++++++++
    local_size = int(nlon * nlat / comm_size)
    offset = comm_rank * local_size
    
    if comm_rank == comm_size - 1:
        local_size = nlon * nlat - offset

    partition = pyoasis.ApplePartition(offset,local_size)
    
    if comm_rank == 0:
        logging.info('  End Of Part Def')
        
    # ++++++++++++++++++++++++
    #   VARIABLES DEFINITION
    # ++++++++++++++++++++++++
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

    # +++++++++++++++++++++
    #   END OF DEFINITION
    # +++++++++++++++++++++
    comp.enddef()
    
    if comm_rank == 0:
        logging.info('  End Of Definition')
        
    # +++++++++++++++++
    #   RUN EXCHANGES
    # +++++++++++++++++
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

    psi = pyoasis.asarray( np.arange(local_size*nlvl).reshape(local_size,nlvl,order='F')+offset+1 )
    phi = pyoasis.asarray( np.arange(local_size*2).reshape(local_size,2,order='F')+offset+1 )
    dxpsi = pyoasis.asarray( np.zeros((local_size,nlvl)) )
    dypsi = pyoasis.asarray( np.zeros((local_size,nlvl)) )
    dxphi = pyoasis.asarray( np.zeros((local_size,2)) )
    dyphi = pyoasis.asarray( np.zeros((local_size,2)) )

    for it in range(niter):
        it_sec = int(time_step * it)
        
        if comm_rank == 0:
            logging.info(f'  Ite {it}:')

        # send field for Modeling
        if it_sec%dat_psi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_psi._name))

        if it_sec%dat_phi.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_phi._name))

        dat_psi.put(it_sec,psi)
        dat_phi.put(it_sec,phi)

        # receive modified field
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
    ref_psi = np.arange(nlon*nlat*nlvl).reshape(nlon,nlat,nlvl,order='F')
    ref_psi = make_edge_psi(ref_psi)
    ref_dxpsi = np.diff(ref_psi,axis=0,append=ref_psi[0:1,:,:])
    ref_dypsi = np.diff(ref_psi,axis=1,prepend=ref_psi[:,0:1,:])
    ref_dxpsi = ref_dxpsi[1:-1,1:-1,:]
    ref_dypsi = ref_dypsi[1:-1,1:-1,:]
    ref_dxpsi = ref_dxpsi.reshape(nlon*nlat,nlvl,order='F')
    ref_dypsi = ref_dypsi.reshape(nlon*nlat,nlvl,order='F')
    py_size = int(nlon * nlat / comm_size)
    for rank in range(comm.Get_size()-comm_size):
        ref_dxpsi[rank*py_size:(rank+1)*py_size,:] = ref_dxpsi[rank*py_size:(rank+1)*py_size,:] + (rank + 1) / 10.
        ref_dypsi[rank*py_size:(rank+1)*py_size,:] = ref_dypsi[rank*py_size:(rank+1)*py_size,:] + (rank + 1) / 10.
    ref_dxpsi = ref_dxpsi[comm_rank*local_size:(comm_rank+1)*local_size,:]
    ref_dypsi = ref_dypsi[comm_rank*local_size:(comm_rank+1)*local_size,:]
    
    
    ref_phi = np.arange(nlon*nlat*2).reshape(nlon,nlat,2,order='F')
    ref_phi = make_edge_phi(ref_phi)
    ref_dxphi = np.diff(ref_phi,axis=0,append=ref_phi[0:1,:,:])
    ref_dyphi = np.diff(ref_phi,axis=1,prepend=ref_phi[:,0:1,:])
    ref_dxphi = ref_dxphi[1:-1,1:-1,:]
    ref_dyphi = ref_dyphi[1:-1,1:-1,:]
    ref_dxphi = ref_dxphi.reshape(nlon*nlat,2,order='F')
    ref_dyphi = ref_dyphi.reshape(nlon*nlat,2,order='F')
    for rank in range(comm.Get_size()-comm_size):
        ref_dxphi[rank*py_size:(rank+1)*py_size,:] = ref_dxphi[rank*py_size:(rank+1)*py_size,:] + (rank + 1) / 10.
        ref_dyphi[rank*py_size:(rank+1)*py_size,:] = ref_dyphi[rank*py_size:(rank+1)*py_size,:] + (rank + 1) / 10.
    ref_dxphi = ref_dxphi[comm_rank*local_size:(comm_rank+1)*local_size,:]
    ref_dyphi = ref_dyphi[comm_rank*local_size:(comm_rank+1)*local_size,:]

    # +++++++++++++++++++
    #      CHECK RES
    # +++++++++++++++++++
    if np.array_equal(ref_dxpsi,dxpsi) and np.array_equal(ref_dypsi,dypsi) and np.array_equal(ref_dxphi,dxphi) and np.array_equal(ref_dyphi,dyphi):
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

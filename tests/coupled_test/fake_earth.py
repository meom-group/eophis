# oasis modules
import pyoasis
from pyoasis import OASIS
from mpi4py import MPI
# utils modules
import f90nml as nml
import numpy
import logging
import time

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
    nlon = 720
    nlat = 603
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
    var_out = ['E_OUT_0','E_OUT_1','E_OUT_2']
    var_in = ['E_IN_0','E_IN_1']

    dat_sst = pyoasis.Var(var_out[0],partition,OASIS.OUT,bundle_size=1)
    dat_svt = pyoasis.Var(var_out[1],partition,OASIS.OUT,bundle_size=nlvl)
    dat_msk = pyoasis.Var(var_out[2],partition,OASIS.OUT,bundle_size=1)
    
    inf_sst = pyoasis.Var(var_in[0],partition,OASIS.IN,bundle_size=1)
    inf_svt = pyoasis.Var(var_in[1],partition,OASIS.IN,bundle_size=nlvl)

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

    sst = pyoasis.asarray( numpy.zeros((local_size,1)) )
    svt = pyoasis.asarray( numpy.zeros((local_size,nlvl)) )
    msk = pyoasis.asarray( numpy.arange(local_size).reshape(local_size,1) )
    var_sst = pyoasis.asarray( numpy.zeros((local_size,1)) )
    var_svt = pyoasis.asarray( numpy.zeros((local_size,nlvl)) )


    for it in range(niter):
        it_sec = int(time_step * it)
        
        if comm_rank == 0:
            logging.info(f'  Ite {it}:')

        # send field for Modeling
        if it_sec%dat_sst.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_sst._name))

        if it_sec%dat_svt.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_svt._name))

        if it_sec%dat_msk.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Static (once) sending of %s' % (dat_msk._name))

        dat_sst.put(it_sec,sst)
        dat_svt.put(it_sec,svt)
        dat_msk.put(it_sec,msk)

        # receive modified field
        if it_sec%inf_sst.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (inf_sst._name))

        if it_sec%inf_svt.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (inf_svt._name))

        inf_sst.get(it_sec,var_sst)
        inf_svt.get(it_sec,var_svt)

        # Modify field
        sst = pyoasis.asarray(var_sst + 0.2)
        svt = pyoasis.asarray(var_svt + 0.5)

    if comm_rank == 0:
        logging.info('  End Of Loop')

    # check final values
    epsilon = 1e-8
    error = abs(var_sst[0,0] - 66833.2) + abs(var_svt[0,2] - 2813.5)

    if error < epsilon:
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

"""
Toy Earth (TE) script emulates a surrogate geoscientific code with an hard-coded OASIS interface.
Purpose of TE is to test Eophis behavior in real conditions, without deploying an entire heavy geoscientific model.
It is coupled with the Python code contained in models.py in which the coupling interface has been deployed by Eophis.
Coupling namelist is also written by Eophis

TE initializes the data and sends them first to the coupled model. Returned data may be compared to expected results.
Coupling, content of TE and models.py may be adapted in order to test different features.


WRITE AND COUPLE
----------------
TE advances in time with parameters provided in "earth_namelist" and sends:
    - one 2D field sst, with a hourly frequency on grid (720,603)
    - one 3D field svt, with a daily frequency on grid (720,603,3)
    - one fixed metric field msk, only once, on the same sst grid

Coupled model adds 100 to sst and svt and returns them as sst_var and svt_var, respectively. They are then copied in sst and svt.
In addition, TE adds 0.2 to sst and 0.5 to svt every time step. Given the number of time steps and exchanges, final values are theoretically known.
Test is successful if final sst and svt correspond to theory.

This test case illustrates a basic coupling. It means that:
    - Eophis objects correctly set up OASIS interface to perform exchanges of 2D and 3D data
    - Data stream is correctly orchestrated between exchanges and coupled model
    - Coupling namelist has been correctly written with right frequencies

"""
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
    nlon = 720
    nlat = 603
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
    var_out = ['E_OUT_0','E_OUT_1','E_OUT_2']
    var_in = ['E_IN_0','E_IN_1']

    dat_sst = pyoasis.Var(var_out[0],partition,OASIS.OUT,bundle_size=1)
    dat_svt = pyoasis.Var(var_out[1],partition,OASIS.OUT,bundle_size=nlvl)
    dat_msk = pyoasis.Var(var_out[2],partition,OASIS.OUT,bundle_size=1)
    
    inf_sst = pyoasis.Var(var_in[0],partition,OASIS.IN,bundle_size=1)
    inf_svt = pyoasis.Var(var_in[1],partition,OASIS.IN,bundle_size=nlvl)

    if comm_rank == 0:
        logging.info('  End Of Var Def')

    # ++++++++++++++++++++++++++++
    #   OASIS: END OF DEFINITION
    # ++++++++++++++++++++++++++++
    comp.enddef()
    
    if comm_rank == 0:
        logging.info('  End Of Definition')
        
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

    # +++++++++++++++++++
    #   INITIALIZE DATA
    # +++++++++++++++++++
    # Set sst and svt data to zero to control evolution
    sst = pyoasis.asarray( numpy.zeros((local_size,1)) )
    svt = pyoasis.asarray( numpy.zeros((local_size,nlvl)) )
    # msk value does not matter since it is sent without return
    msk = pyoasis.asarray( numpy.arange(local_size).reshape(local_size,1) )
    # Reception fields initialized to zero
    var_sst = pyoasis.asarray( numpy.zeros((local_size,1)) )
    var_svt = pyoasis.asarray( numpy.zeros((local_size,nlvl)) )

    # +++++++++++++++++
    #   RUN EXCHANGES
    # +++++++++++++++++
    # Loop for time advancement
    for it in range(niter):
        it_sec = int(time_step * it)
        
        if comm_rank == 0:
            logging.info(f'  Ite {it}:')

        # send fields
        if it_sec%dat_sst.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_sst._name))

        if it_sec%dat_svt.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Sending %s' % (dat_svt._name))

        if it_sec%dat_msk.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Static (once) sending of %s' % (dat_msk._name))

        dat_sst.put(it_sec,sst)
        dat_svt.put(it_sec,svt)
        dat_msk.put(it_sec,msk)

        # receive fields
        if it_sec%inf_sst.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (inf_sst._name))

        if it_sec%inf_svt.cpl_freqs[0] == 0.0 and comm_rank == 0:
            logging.info('    Receiving %s' % (inf_svt._name))

        inf_sst.get(it_sec,var_sst)
        inf_svt.get(it_sec,var_svt)

        # Modify fields
        sst = pyoasis.asarray(var_sst + 0.2)
        svt = pyoasis.asarray(var_svt + 0.5)

    if comm_rank == 0:
        logging.info('  End Of Loop')

    # +++++++++++++++
    #   FINAL CHECK
    # +++++++++++++++
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

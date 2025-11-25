"""
Toy Earth (TE) script emulates a surrogate geoscientific code with an hard-coded OASIS interface.

First, it reads 'namcouple' and 'eophis_nml' (both auto-generated) to get information about coupling context defined in Eophis main script.
From those information, TE initializes and performs right number of exchanges with randomly filled arrays in accordance with defined coupling.
This way, TE adapts its behavior with the eophis main script.

Purpose is to test or help track bug in the Eophis main script by isolating it from a whole geophyscial Fortran model.


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
import math


def main():
    """ Main steps of Toy Earth. """
    # +++++++++++++++++++++++++
    #   OASIS: INITIALISATION
    # +++++++++++++++++++++++++
    comm = MPI.COMM_WORLD
    component_name = "toy_earth"
    comp = pyoasis.Component(component_name,True,comm)
    comm = comp.localcomm
    comm_rank = comp.localcomm.rank
    comm_size = comp.localcomm.size


    # ++++++++++++++++++++++
    #   INFO FROM NAMELIST
    # ++++++++++++++++++++++
    if comm_rank == 0:
        # eophis_nml
        namelist = nml.read('eophis_nml')
        nb_var = namelist['nameophis_nb']['nb_var']
        cpl_names = namelist['nameophis_var']['cpl_names']
        cpl_ins = namelist['nameophis_var']['cpl_ins']
        cpl_aliases = namelist['nameophis_var']['cpl_aliases']
        cpl_lvls = namelist['nameophis_var']['cpl_lvls']

        # namcouple
        with open('namcouple', 'r') as infile:
            lines = (infile.read()).split("\n")
    
        # time inf
        step = 1e8
        total_time = 0
        for alias in cpl_aliases:
            pos = [i for i,txt in enumerate(lines) if alias in txt][0]
            step = min( step , int( lines[pos].split()[3] ) )
            total_time = max( total_time , int( lines[pos].split()[3] ) )
    
        niter = math.floor(total_time / step)
    
        # Grid size
        nlon, nlat = int( lines[pos+1].split()[0] ), int( lines[pos+1].split()[1] )
    
    else:
        nb_var, total_time, step, niter, nlon, nlat = 0,0.0,0,0,0,0
        cpl_names, cpl_aliases, cpl_ins, cpl_lvls = [],[],[],[]
    
    # Communicate
    nb_var, step, niter, nlon, nlat = comm.bcast(nb_var,root=0), comm.bcast(nlon,root=0), comm.bcast(nlat,root=0)
    step, niter, total_time = comm.bcast(step,root=0), comm.bcast(niter,root=0), comm.bcast(total_time,root=0)
    cpl_names, cpl_aliases = comm.bcast(cpl_names,root=0), comm.bcast(cpl_aliases,root=0)
    cpl_ins, cpl_lvls = comm.bcast(cpl_ins,root=0), comm.bcast(cpl_lvls,root=0)

    nlvl = max(cpl_lvls)
    

    # +++++++++++++++++++++++++++++++
    #   OASIS: PARTITION DEFINITION
    # +++++++++++++++++++++++++++++++
    if comm_rank == 0:
        logging.info('  Grid size: %.1i %.1i %.1i' % (nlon, nlat, nlvl))
        logging.info('  Define Partition from grid')
    
    local_size = int(nlon * nlat / comm_size)
    offset = comm_rank * local_size
    if comm_rank == comm_size - 1:
        local_size = nlon * nlat - offset

    partition = pyoasis.ApplePartition(offset,local_size)
        
    if comm_rank == 0:
        logging.info('  End Of Partition definition')


    # +++++++++++++++++
    #   DEFINE FIELDS
    # +++++++++++++++++
    # -- sending field --
    outfld = np.random.rand(local_size,nlvl).astype('float32')
    
    # -- receiving field --
    infld = np.zeros(local_size,nlvl).astype('float32')


    # +++++++++++++++++++++++++++++++
    #   OASIS: VARIABLES DEFINITION
    # +++++++++++++++++++++++++++++++
    var_out = {}
    var_in = {}
    
    for varname, alias, to_rcv, lvl in zip(cpl_names,cpl_aliases,cplins,cpl_lvls):
        if to_rcv:
            var_out.update{ varname : pyoasis.Var(alias,partition,OASIS.OUT,bundle_size=lvl) }
        else:
            var_in.update{ varname : pyoasis.Var(alias,partition,OASIS.IN,bundle_size=lvl) }
    
    if comm_rank == 0:
        logging.info(f'  Toy Earth coupled with following variables:')
        logging.info(f'     OUT: {var_out.keys()}')
        logging.info(f'     IN: {var_in.keys()}')

    if comm_rank == 0:
        logging.info('  End Of Var Def')


    # ++++++++++++++++++++++++++++
    #   OASIS: END OF DEFINITION
    # ++++++++++++++++++++++++++++
    comp.enddef()
    
    if comm_rank == 0:
        logging.info('  End Of Definition')
        
    if comm_rank == 0:
        logging.info('  -----------------------------------------------------------')
        logging.info('  Number of iterations: %.1i' % niter)
        logging.info('  Time step: %.1i' % step)
        logging.info('  Simulation length: %.1i' % total_time)
        logging.info('  -----------------------------------------------------------')


    # +++++++++++++++++
    #   RUN EXCHANGES
    # +++++++++++++++++
    # Loop for time advancement
    for it in range(niter):
        it_sec = int(step * it)
        
        if comm_rank == 0:
            logging.info(f'  Ite {it}:')

        # ------ Send fields ------- #
        for varname, var in var_out.items():
            if it_sec%var.cpl_freq[0] == 0.0:
                if comm_rank == 0:
                    logging.info('    Sending %s - %s' % (varname,var._name))
                var.put(it_sec,pyoasis(outfld[:,:,0:var.bundle_size]))
        
        # ------ Receive fields ------- #
        for varname, var in var_in.items():
            if it_sec%var.cpl_freq[0] == 0.0:
                if comm_rank == 0:
                    logging.info('    Sending %s - %s' % (varname,var._name))
                var.get(it_sec,pyoasis(infld[:,:,0:var.bundle_size]))


    if comm_rank == 0:
        logging.info('  End Of Loop')

    # +++++++++++++++++++++++++
    #        TERMINATION
    # +++++++++++++++++++++++++
    del comp

    if comm_rank == 0:
        logging.info('  End Of Toy Earth Program - SUCCESSFUL')


if __name__=="__main__":
    # Init log file
    logging.basicConfig(filename='earth.log',encoding='utf-8',level=logging.INFO)
    main()

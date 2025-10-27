"""
Toy Earth (TE) script emulates a surrogate geoscientific code with an hard-coded OASIS interface.
It initializes three dimensionless physical 3D fields U, V, T, discretized on metric 2D fields X, Y that represent the simulated domain.
TE advances in time in accordance with parameters provided in earth_namelist_tuto and updates the physical fields with the following equation:

A = A + dt**2 / 100. * B

Where A is one of the abovementioned physical fields and B a forcing term corresponding to A.

The model can be executed in two distinct modes:
    - standalone: B is imposed with a constant value. OASIS interface is disabled.
    - coupled: OASIS interface is activated and Toy Earth can send the physical and metric fields through OASIS.
               It can also receive up to three forcing fields. If a forcing field is received, it is used instead of B for time advancement.

It is then possible to change the way the physical fields are forced. The only condition is to compute the forcing terms in an external script and to exchange results through OASIS.

"""
# oasis modules
import pyoasis
from pyoasis import OASIS
from mpi4py import MPI
# utils modules
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import f90nml as nml
import numpy as np
import logging
import time

def gather_field(local_array,dim1,dim2,dim3,comm,rank,size):
    """ Gather physical fields distributed among processes in local_array (numpy.ndarray) to Master process (rank 0) with MPI. """
    if rank == 0:
        # Master process collect all local array from all other processes
        collected_arrays = [np.empty((local_array.shape[0],dim3), dtype=np.float64) for _ in range(size)]
        collected_arrays[0] = local_array
        for i in range(1,size):
            comm.Recv(collected_arrays[i], source=i, tag=77)
        return np.concatenate(collected_arrays,axis=0).reshape(dim1,dim2,dim3)
    else:
        # Other processes send their local array
        comm.Send(local_array, dest=0, tag=77)
        return -1


def plot_field(array,lon,lat,cmap,outfile,vmin,vmax):
    """ Plot a color map of array (numpy.ndarray). """
    # figure
    plt.figure(figsize=(12,8))
    ax = plt.axes()
    # color map
    pcm = ax.pcolormesh(lon,lat,array[:,:,0], cmap=cmap, norm=colors.Normalize(vmin=vmin, vmax=vmax))
    cbar = plt.colorbar(pcm, ax=ax, orientation='vertical', pad=0.05, shrink=0.5)
    # write fig
    plt.savefig(outfile, bbox_inches='tight')
    plt.close()


def main():
    """ Main steps of Toy Earth. """
    # ++++++++++++++++++++++
    #   INFO FROM NAMELIST
    # ++++++++++++++++++++++
    namelist = nml.read('earth_namelist_tuto')
    
    # runtime
    time_step = int( namelist['namdom']['rn_Dt'] )
    niter = int( namelist['namrun']['nn_itend'] - namelist['namrun']['nn_it000'] ) + 1
    nn_write = int( namelist['namrun']['nn_write'] )
    total_time = niter*time_step
    
    # domain
    nlon = int( namelist['namdom']['nlon'] )
    nlat = int( namelist['namdom']['nlat'] )
    nlvl = int( namelist['namdom']['nlvl'] )
    
    # coupling
    ln_cpl = namelist['namcpl']['ln_cpl']
    cpl_u = namelist['namcpl']['cpl_u']
    cpl_v = namelist['namcpl']['cpl_v']
    cpl_t = namelist['namcpl']['cpl_t']
    cpl_x = namelist['namcpl']['cpl_x']
    cpl_y = namelist['namcpl']['cpl_y']
    cpl_force_u = namelist['namcpl']['cpl_force_u']
    cpl_force_v = namelist['namcpl']['cpl_force_v']
    cpl_force_t = namelist['namcpl']['cpl_force_t']
    
    # check consistency
    cpl_u[1] = cpl_u[1] * ln_cpl
    cpl_v[1] = cpl_v[1] * ln_cpl
    cpl_t[1] = cpl_t[1] * ln_cpl
    cpl_x[1] = cpl_x[1] * ln_cpl
    cpl_y[1] = cpl_y[1] * ln_cpl
    cpl_force_u[1] = cpl_force_u[1] * ln_cpl
    cpl_force_v[1] = cpl_force_v[1] * ln_cpl
    cpl_force_t[1] = cpl_force_t[1] * ln_cpl

    # +++++++++++++++++++++++++
    #   OASIS: INITIALISATION
    # +++++++++++++++++++++++++
    comm = MPI.COMM_WORLD
    component_name = "toy_earth"
    if ln_cpl:
        comp = pyoasis.Component(component_name,True,comm)
        comm = comp.localcomm
        comm_rank = comp.localcomm.rank
        comm_size = comp.localcomm.size
    else:
        comm_rank = comm.Get_rank()
        comm_size = comm.Get_size()
    
    if comm_rank == 0 and ln_cpl:
        logging.info('  -----------------------------------------------------------')
        logging.info('  Component name %s with ID: %.1i' % (component_name,comp._id))
        logging.info('  Running with %.1i processes' % comm_size)
        logging.info('  -----------------------------------------------------------')

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

    if ln_cpl:
        partition = pyoasis.ApplePartition(offset,local_size)
        
    if comm_rank == 0:
        logging.info('  End Of Partition definition')

    # +++++++++++++++++
    #   DEFINE FIELDS
    # +++++++++++++++++
    # -- metrics --
    x0, y0 = np.linspace(0.,90.,nlon), np.linspace(-45.,45.,nlat)
    x1, y1 = np.meshgrid(x0,y0,indexing='xy')
    x = np.reshape(x1,nlon*nlat)[offset:offset+local_size]
    y = np.reshape(y1,nlon*nlat)[offset:offset+local_size]
    
    # -- physical fields --
    # U velocity
    u0 = 2.0 + np.sin(2.0 * x * 0.0175) ** 4.0 * np.cos(4.0 * y * 0.0175)
    u = np.zeros(u0.shape+(nlvl,))
    u[:,0] = u0
    for lvl in range(1,nlvl):
        u[:,lvl] = u[:,lvl-1] / lvl
    umin0, umax0 = u.min(), u.max()
    # V velocity
    v0 = 2.0 - np.cos(3.1415 * (np.arccos(np.cos(y * 0.0175) * np.cos(x * 0.0175)) / 3.77))
    v = np.zeros(v0.shape+(nlvl,))
    v[:,0] = u0
    for lvl in range(1,nlvl):
        v[:,lvl] = v[:,lvl-1] / lvl
    vmin0, vmax0 = v.min(), v.max()
    # temperature
    t0 = y * 0.2
    t = np.zeros(t0.shape+(nlvl,))
    t[:,0] = t0
    for lvl in range(1,nlvl):
        t[:,lvl] = t[:,lvl-1] / 2.0
    tmin0, tmax0 = t.min(), t.max()
    
    # -- Reception field --
    tmp  = pyoasis.asarray( np.zeros((local_size,nlvl)) )

    # +++++++++++++++++++++++++++++++
    #   OASIS: VARIABLES DEFINITION
    # +++++++++++++++++++++++++++++++
    var_out = []
    var_in = []
    
    if cpl_u[1]:
        dat_u = pyoasis.Var(cpl_u[2],partition,OASIS.OUT,bundle_size=min(nlvl,cpl_u[3]))
        var_out.append(cpl_u[2])

    if cpl_v[1]:
        dat_v = pyoasis.Var(cpl_v[2],partition,OASIS.OUT,bundle_size=min(nlvl,cpl_v[3]))
        var_out.append(cpl_v[2])
        
    if cpl_t[1]:
        dat_t = pyoasis.Var(cpl_t[2],partition,OASIS.OUT,bundle_size=min(nlvl,cpl_t[3]))
        var_out.append(cpl_t[2])

    if cpl_x[1]:
        dat_x = pyoasis.Var(cpl_x[2],partition,OASIS.OUT,bundle_size=min(nlvl,cpl_x[3]))
        var_out.append(cpl_x[2])

    if cpl_y[1]:
        dat_y = pyoasis.Var(cpl_y[2],partition,OASIS.OUT,bundle_size=min(nlvl,cpl_y[3]))
        var_out.append(cpl_y[2])
    # ------------- #
    if cpl_force_u[1]:
        dat_force_u = pyoasis.Var(cpl_force_u[2],partition,OASIS.IN,bundle_size=min(nlvl,cpl_force_u[3]))
        var_in.append(cpl_force_u[2])
        
    if cpl_force_v[1]:
        dat_force_v = pyoasis.Var(cpl_force_v[2],partition,OASIS.IN,bundle_size=min(nlvl,cpl_force_v[3]))
        var_in.append(cpl_force_v[2])

    if cpl_force_t[1]:
        dat_force_t = pyoasis.Var(cpl_force_t[2],partition,OASIS.IN,bundle_size=min(nlvl,cpl_force_t[3]))
        var_in.append(cpl_force_t[2])

    if comm_rank == 0:
        logging.info(f'  Toy Earth coupled with following namcouple variables:')
        logging.info(f'     OUT: {var_in}')
        logging.info(f'     IN: {var_out}')

    if comm_rank == 0:
        logging.info('  End Of Var Def')

    # ++++++++++++++++++++++++++++
    #   OASIS: END OF DEFINITION
    # ++++++++++++++++++++++++++++
    if ln_cpl:
        comp.enddef()
    
    if comm_rank == 0:
        logging.info('  End Of Definition')
        
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

        # ------ Send fields ------- #
        if cpl_u[1]:
            if it_sec%dat_u.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Sending %s' % (dat_u._name))
            dat_u.put(it_sec,pyoasis.asarray(u))

        if cpl_v[1]:
            if it_sec%dat_v.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Sending %s' % (dat_v._name))
            dat_v.put(it_sec,pyoasis.asarray(v))

        if cpl_t[1]:
            if it_sec%dat_t.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Sending %s' % (dat_t._name))
            dat_t.put(it_sec,pyoasis.asarray(t))

        if cpl_x[1]:
            if it_sec%dat_x.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Sending %s' % (dat_x._name))
            dat_x.put(it_sec,pyoasis.asarray(x))

        if cpl_y[1]:
            if it_sec%dat_y.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Sending %s' % (dat_y._name))
            dat_y.put(it_sec,pyoasis.asarray(y))

        # ------ Receive fields ------- #
        force_u = 0.02 * np.ones((local_size,nlvl))
        if cpl_force_u[1]:
            if it_sec%dat_force_u.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Receiving %s' % (dat_force_u._name))
            dat_force_u.get(it_sec,tmp)
            force_u[:,0:dat_force_u.bundle_size] = tmp[:,0:dat_force_u.bundle_size]
            
        force_v = 0.05 * np.ones((local_size,nlvl))
        if cpl_force_v[1]:
            if it_sec%dat_force_v.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Receiving %s' % (dat_force_v._name))
            dat_force_v.get(it_sec,tmp)
            force_v[:,0:dat_force_u.bundle_size] = tmp[:,0:dat_force_v.bundle_size]

        force_t = 0.1 * np.ones((local_size,nlvl))
        if cpl_force_t[1]:
            if it_sec%dat_force_t.cpl_freqs[0] == 0.0 and comm_rank == 0:
                logging.info('    Receiving %s' % (dat_force_t._name))
            dat_force_t.get(it_sec,tmp)
            force_t[:,0:dat_force_u.bundle_size] = tmp[:,0:dat_force_t.bundle_size]

        # ------ Advance fields -------
        u = u + time_step**2 * force_u / 100.
        v = v + time_step**2 * force_v / 100.
        t = t + time_step**2 * force_t / 100.

        # ------ Plot fields ------ #
        if it%nn_write == 0.0:
            ufull = gather_field(u,nlon,nlat,nlvl,comm,comm_rank,comm_size)
            vfull = gather_field(v,nlon,nlat,nlvl,comm,comm_rank,comm_size)
            tfull = gather_field(t,nlon,nlat,nlvl,comm,comm_rank,comm_size)
            
            if comm_rank == 0:
                logging.info('    Output fields')
                plot_field(ufull,x0,y0,'viridis',cpl_u[0]+'_'+str(it)+'.png',umin0,umax0)
                plot_field(vfull,x0,y0,'viridis',cpl_v[0]+'_'+str(it)+'.png',vmin0,vmax0)
                plot_field(tfull,x0,y0,'plasma',cpl_t[0]+'_'+str(it)+'.png',tmin0,tmax0)


    if comm_rank == 0:
        logging.info('  End Of Loop')

    # +++++++++++++++++++++++++
    #        TERMINATION
    # +++++++++++++++++++++++++
    if ln_cpl:
        del comp

    if comm_rank == 0:
        logging.info('  End Of Toy Earth Program')


if __name__=="__main__":
    # Init log file
    logging.basicConfig(filename='earth.log',encoding='utf-8',level=logging.INFO)
    main()

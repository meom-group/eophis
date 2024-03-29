Usage
=====

.. autosummary::
   :toctree: generated



Eophis Environment
------------------
::

    # eophis API
    import eophis
    from eophis import Freqs, Grids


Logs
~~~~
::

    eophis.infos()
    eophis.warning()
    eophis.abort()



Tunnel Registration
~~~~~~~~~~~~~~~~~~~
::

    tunnel_config = list()
    tunnel_config.append( { 'label' : 'TO_EARTH', \
                            'grids' : { 'eORCA05' : Grids.eORCA05, \
                                        'lmdz' : (180,151,0,0)  }, \
                            'exchs' : [ {'freq' : Freqs.HOURLY, 'grd' : 'eORCA05', 'lvl' : 1, 'in' : ['sst'], 'out' : ['sst_var'] },  \
                                        {'freq' : Freqs.DAILY,  'grd' : 'eORCA05', 'lvl' : 3, 'in' : ['svt'], 'out' : ['svt_var'] },  \
                                        {'freq' : Freqs.STATIC, 'grd' : 'eORCA05', 'lvl' : 1, 'in' : ['msk'], 'out' : [] } ] }
            # optional      'es_aliases' : { 'sst' : 'EAR_SST', 'svt' : 'EAR_TEMP', 'sst_var' : 'EAR_SSTV', 'svt_var' : 'EARTEMPV'},  \
            # optional      'im_aliases' : { 'sst' : 'EOP_SST', 'svt' : 'EOP_TEMP', 'sst_var' : 'EOP_SSTV', 'svt_var' : 'EOPTEMPV'}   }
                        )

    earth = eophis.register_tunnels( tunnel_config )

Read Fortran Namelist
~~~~~~~~~~~~~~~~~~~~~

  .. code-block:: bash
  
     vi earth_namelist
     !-----------------------------------------------------------------------
     &namrun        !   parameters of the run
     !-----------------------------------------------------------------------
        nn_it000      =    1    !  first time step
        nn_itend      =    2000 !  last  time step
     /
     !-----------------------------------------------------------------------
     &namdom        !   time and space domain
     !-----------------------------------------------------------------------
        rn_Dt       =    1200. ! time step value
     /


::

    earth_nml = eophis.FortranNamelist('~/home/earth_namelist')
    step, it_end, it_0 = earth_nml.get('rn_Dt','nn_itend','nn_it000')
    total_time = (it_end - it_0 + 1) * step



Preproduction Mode
------------------
::

    set_mode('preprod')


Write Namelists
~~~~~~~~~~~~~~~

OASIS namcouple
'''''''''''''''
::

    write_coupling.namelist( simulation_time=total_time )

Fortran Namelist
''''''''''''''''
`...WORK IN PROGRESS...`


Production Mode
---------------
::

    set_mode('prod')


Setup Coupling
~~~~~~~~~~~~~~~
::

    open_tunnels()
    close_tunnels()

Import Models
~~~~~~~~~~~~~
::

    from models import add_100


**A model must fit the following requisites and structure :**
    1. must be a callable function that takes N numpy arrays as inputs
    2. returns N None for the N awaited outputs if at least one of the input is None
    3. inputs may be freely formatted and transformed into what you want BUT...
    4. ...outputs must be formatted as numpy array for sending back

::

    import numpy as np

    #             Utils            #
    # ++++++++++++++++++++++++++++ #
    def Is_None(*inputs):
        """ Test presence of at least one None in inputs """
        return any(item is None for item in inputs)

    # ============================ #
    #          Add Hundred         #
    # ============================ #
    def add_100(sst):
        """ Trivially add 100 to sst (numpy.ndarray) """
        if Is_None(sst):
            return None
        else:
            return np.add(sst,100)


Assemble Time Loop
~~~~~~~~~~~~~~~~~~
::

    @eophis.all_in_all_out(earth_system=earth, step=step, niter=niter)
    def loop_core(**inputs):
        outputs = {}
        outputs['sst_var'] = add_100(inputs['sst'])
        outputs['svt_var'] = add_100(inputs['svt'])
        return outputs

Static Exchanges
~~~~~~~~~~~~~~~~
::

    earth.receive('msk')
    earth.send()


Regular Exchanges
~~~~~~~~~~~~~~~~~
::

    eophis.tunnels_ready()
    eophis.starter(loop_core)


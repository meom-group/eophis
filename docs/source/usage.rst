Usage
=====

.. autosummary::
   :toctree: generated

In this section, we present how to use the functions and objects provided by Eophis with coding examples.


.. note:: For a better understanding of the Eophis abstraction environment, please read the **Concepts** section.

The presented examples rely on the **Write and Couple** test case provided with the library in the Github repository and described in the **Tests** section. Keep in mind that this is not a tutorial for the test case. It is used to illustrate the documentation.


Eophis Environment
------------------
Eophis package must be imported before anything else with the following command:

::

    # - main.py
    import eophis
    

This automatically creates the log files ``eophis.out`` and ``eophis.err``. The latter is left empty while the first one is filled with informations about Eophis version, dependencies and Python implementation.


.. code-block:: bash

    cat eophis.out
    ===============================
    |    CNRS - IGE - MEOM Team   |
    |           ------            |
    |     EOPHIS 1.0.0 (2024)     |
    ===============================
    Main packages used:
    Python implementation: CPython
    Python version       : 3.10.4
    IPython version      : 7.32.0

    mpi4py: 3.1.5
    f90nml: 1.4.4
    numpy : 1.26.4

    ---------------------------
      Coupling Initialization
    ---------------------------
      Checking up OASIS namelists...
          namcouple not found, looking for reference file namcouple_ref
          namcouple_ref not found either, creating it from scratch
      Reading namcouple


Note the few lines about *Coupling Initialization*. When Eophis starts, it automatically looks for the OASIS coupling namelist ``namcouple`` to read its content.

Several scenarios may occur:
    - ``namcouple`` exists alone: it is read and copied as ``namcouple_ref`` for original footprint
    - ``namcouple`` does not exist but ``namcouple_ref`` does: ``namcouple_ref`` is copied as ``namcouple``, then read
    - both files exist: ``namcouple`` is read
    - both files does not exist: Eophis creates an empty ``namcouple`` and reads it

A last scenario is if ``namcouple`` exists but is stored elsewhere. Indeed, default reading phase considers that the namelists to look for are stored in the execution directory. To read a coupling namelist stored in another directory, reading of ``namcouple`` must be done with:

::

    import eophis
    # namcouple file is not found and is initialized from scratch
    
    namcouple_input_path = '/PATH/TO/REMOTE/namcouple'
    namcouple_output_path = '/PATH/WHERE/TO/OUTPUT/NAMCOUPLE/LATER/OR/NOT/namcouple'

    eophis.init_namcouple( namcouple_input_path, namcouple_output_path )

    # Eophis is now working with content of remote namcouple.


Note that this is ``eophis.init_namcouple()`` with execution directory as arguments that is called at the start of Eophis. Thoses features allow the user to write himself the coupling namelist.


.. seealso:: Let's say that the user expects to deploy a Python model within an ocean model that is also coupled with an atmosphere model with OASIS. Since only one coupling namelist is required by OASIS to perform all the exchanges, the user may bring ``namcouple`` in the execution directory with pre-written informations about the ocean/atmosphere coupling and use Eophis to complete it with the Python coupling informations. Original ``namcouple`` will be saved under ``namcouple_ref``.

If the user does not know about ``namcouple`` or does not wish to write it, the default case keeps the creation of the OASIS namelist straightforward.



Logs
~~~~
To write messages in the log files, use the following commands:

::

    eophis.info('Hello World, my name is Eophis')
    eophis.warning('Beware of negative numbers')
    eophis.abort('ERROR with sst dimensions')

Note that ``eophis.abort()`` will also kill the execution. Here are the outputs:

.. code-block:: bash

    cat eophis.out
    ===============================
    |    CNRS - IGE - MEOM Team   |
    |           ------            |
    |     EOPHIS 1.0.0 (2024)     |
    ===============================
    Main packages used:
    Python implementation: CPython
    Python version       : 3.10.4
    IPython version      : 7.32.0

    mpi4py: 3.1.5
    f90nml: 1.4.4
    numpy : 1.26.4

    ---------------------------
      Coupling Initialization
    ---------------------------
      Checking up OASIS namelists...
          namcouple not found, looking for reference file namcouple_ref
          namcouple_ref not found either, creating it from scratch
      Reading namcouple
      
    Hello World, my name is Eophis
      
    Warning raised by rank 0 ! See error log for details

    RUN ABORTED by rank 0 see error log for details


.. code-block:: bash

    cat eophis.err
    WARNING [RANK:0] from /PATH/TO/SCRIPT/DIR/main.py at line 4:   Beware of negative numbers
    ERROR [RANK:0] from /PATH/TO/SCRIPT/DIR/main.py at line 5:   ERROR with sst dimensions



Import Models
~~~~~~~~~~~~~
Hereunder is the Model ``add_100()`` written in ``models.py`` with the correct requisites described in the **Concepts** section.

::

    # - models.py
    import numpy as np

    #             Utils            #
    # ++++++++++++++++++++++++++++ #
    def Is_None(*inputs):
        """ Test presence of at least one None in inputs """
        return any(item is None for item in inputs)

    # ============================ #
    #          Add Hundred         #
    # ============================ #
    def add_100(field):
        """ Trivially add 100 to field (numpy.ndarray) """
        if Is_None(field):
            return None
        else:
            return np.add(field,100)

Import a Model to be used by Eophis is of course straightforward.

::

    # - main.py
    from models import add_100



Modes
~~~~~
Eophis can be used in preproduction or production mode which have different purposes.

    - Preproduction mode enables namelists editing. It corresponds to a stage where the coupling material needs to be configured. OASIS initialization is disabled in that mode.
    
    
    - Production mode freezes namelists in *read-only*. It corresponds to a stage where the coupling material is ready for execution. Editing tools can be used to check the correspondance between the content of the read namelists with the Tunnels defined in the Eophis script. OASIS may be initialized and coupling started only in that mode.
    
Switching mode is done with the following commands:

::

    eophis.set_mode('preprod')
    eophis.set_mode('prod')

.. warning :: It is strongly recommended to execute two independent instances of Eophis if you plan to use both modes. Using editing tools and directly switching to production mode to start coupling means that the geoscientific code also started and read the namelists before or during editing. In this situation, each script potentially did not read the same informations, which could lead to hazardous results.


    Structure of ``main.py`` shows an example of separated instructions based on the selected mode.
        
    ::
        
        import eophis
        
        def preproduction():
            # [...]

        def production():
            # [...]

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


Read Fortran Namelist
~~~~~~~~~~~~~~~~~~~~~
Fortran namelists may be read both in preproduction and production modes. Hereunder is the content of ``earth_namelist`` with which our surrogate geoscientific model ``fake_earth.py`` will perform the simulation.

  .. code-block:: bash
  
     cat earth_namelist
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


We wish to know the total simulation time in ``main.py`` too. We instantiate a ``FortranNamelist`` and read the values of ``nn_it000``, ``nn_itend`` and ``rn_Dt`` as follows:

::

    earth_nml = eophis.FortranNamelist('~/PATH/TO/earth_namelist')
    step, it_end, it_0 = earth_nml.get('rn_dt','nn_itend','nn_it000')
    total_time = (it_end - it_0 + 1) * step

Note that the ``FortranNamelist.get()`` method is not sensitive to the letter case.



Grids
~~~~~
A Grid may be created both in preproduction and production modes. However, it is not possible to directly instantiate a Grid with the class constructor. This step is done by Tunnel (see hereafter).

A Grid is defined with arguments arranged in a dictionary:
    - number of longitude and latitude points: ``{ 'npts' : () }``
    - number of halos : ``{ 'halos' : }``
    - boundary conditions in east-west and north-south directions: ``{ 'bnd' : () }``
    - grid and folding type, respectively (NorthFold condition only) : ``{ 'folding' : () }``


The fields exchanged with Fake Earth are all discretized on the same global grid whose number of longitude and latitude points are ``720`` and ``603``, respectively. Only first argument ``npts`` is compulsory, others are optional:

::

    my_grid = { 'npts' : (720,603)}


This size corresponds to an eORCA05 grid that is commonly used for global ocean circulation. It is pre-registered in Eophis and can be imported with:

::

    from eophis import Domains

    my_grid = Domains.demo
    print(my_grid)
    
::

    {'npts': (720, 603), 'halos': 0, 'bnd': ('close', 'close'), 'folding': ('T', 'T')}

Fields discretized on this grid will be received without extra halo cells. It can still be modified before sending back, but operations that require neighboring cells won't be executed optimaly on the edges of the local grid. The same eORCA05 grid is also pre-registered in Eophis with halos:

::

    from eophis import Domains
    
    my_halo_grid = Domains.eORCA05
    print(my_halo_grid)
    
::

    {'npts': (720, 603), 'halos': 1, 'bnd': ('cyclic', 'nfold'), 'folding': ('T', 'T')}

Fields discretized on this grid will be received with 1 extra halo cells, with a cyclic boundary condition applied on east-west dimension, and a NorthFold condition for north-south dimension.

Check out the ``eophis.domain.grid`` module described in the **API** section of this documentation for more details about pre-registered Domains.



Tunnel
~~~~~~

Tunnel arguments
''''''''''''''''
A Tunnel may be created both in preproduction and production modes. Since the required arguments are many, it is easier to arrange them in a dictionary:

::

    tunnel_args = { 'label' : '', \
                    'grids' : {}, \
                    'exchs' : [ {} ]
                  }

* ``label`` is the name of the Tunnel
* ``grids`` are the Grids that will be partionned by OASIS and on which fields could be exchanged
* ``exchs`` is a list of parameters that described how the fields should be exchanged

In the previous section, we defined the Grid on which we wish to perform the coupling with Fake Earth, let's use it in Tunnel:

::

    from eophis import Domains

    tunnel_args = { 'label' : 'TO_EARTH', \
                    'grids' : { 'demo' : Domains.demo }, \
                    'exchs' : [ {} ]
                  }

Now, the Tunnel will be able to configure communications of fields discretized on the ``demo`` Grid.

.. note:: More than one Grid may be associated to the Tunnel.

It now remains to define the exchanges. An exchange is characterized by:

* a frequency expressed in seconds: ``{ 'freq' : }``
* a grid on which it occurs: ``{ 'grd' :  }``
* the grid depth: ``{ 'lvl' :  }``
* named received fields: ``{ 'in' : [] }``
* named sent fields: ``{ 'out' : [] }``

::

    exch_1 = {'freq' : 150 , 'grd' : 'geo_grid' , 'lvl' : 5, 'in' : ['f0'], 'out' : ['f1','f2']}

    
In the above example, the line may be read as:

    ``exch_1`` executes every ``150`` seconds, the receiving of field ``f0``
    and the sending back of fields ``f1``, ``f2`` on the first ``5`` levels
    of grid ``geo_grid``.


A Tunnel can handle exchanges with different options, that's why it takes a list as argument. In accordance with the ``write_and_couple`` test case, we finally have the complete Tunnel arguments:

::

    from eophis import Domains, Freqs

    tunnel_args = { 'label' : 'TO_EARTH', \
                  'grids' : { 'demo' : Domains.demo }, \
                  'exchs' : [ {'freq' :        3600,  'grd' : 'demo', 'lvl' : 1, 'in' : ['sst'], 'out' : ['sst_var'] },  \
                              {'freq' : Freqs.DAILY,  'grd' : 'demo', 'lvl' : 3, 'in' : ['svt'], 'out' : ['svt_var'] },  \
                              {'freq' : Freqs.STATIC, 'grd' : 'demo', 'lvl' : 1, 'in' : ['msk'], 'out' : [] }]
                }
                              

Note here that we used pre-registered frequency values. Check out the ``eophis.utils.params`` module described in the **API** section of this documentation fore more details about pre-registered Frequencies.



Tunnel Registration
'''''''''''''''''''
Although direct instantiation of a Tunnel with the class constructor is possible, it is yet not recommended. Indeed, the creation of a Tunnel does not configure the OASIS entities wrapped inside. This can be done only once OASIS is initialized and requires a good knowledge of the coupling and parallel environment.

It is more convenient to use the Tunnel registration interface ``eophis.register_tunnels()``. In addition to Tunnel instantiation, it generates the ``namcouple`` content required for the OASIS entities encapsulated in the Tunnel. Moreover, it allows Eophis to be aware of the Tunnel and to configure it automatically.

Registration takes the same arguments as the Tunnel constructor except that they must be gathered as a list item. This way, it is possible to register several Tunnels in one call. It is also convenient to scatter the exchanges. For example: a Tunnel for the regular exchanges and a Tunnel for the static exchanges:


::

    from eophis import Freqs, Domains

    # empty Tunnel config list
    tunnel_config = list()
    
    # Tunnel for the regular exchanges
    tunnel_config.append( { 'label' : 'TO_EARTH', \
                            'grids' : { 'demo' : Domains.demo }, \
                            'exchs' : [ {'freq' :        3600,  'grd' : 'demo', 'lvl' : 1, 'in' : ['sst'], 'out' : ['sst_var'] }, \
                                        {'freq' : Freqs.DAILY,  'grd' : 'demo', 'lvl' : 3, 'in' : ['svt'], 'out' : ['svt_var'] }] }
                        )

    # Tunnel for the static exchange
    tunnel_config.append( { 'label' : 'TO_EARTH_METRIC', \
                            'grids' : { 'demo' : Domains.demo}, \
                            'exchs' : [ {'freq' : Freqs.STATIC, 'grd' : 'demo', 'lvl' : 1, 'in' : ['msk'], 'out' : []} ] }
                        )

    # Register Tunnels
    earth, earth_metrics = eophis.register_tunnels( tunnel_config )


Grids associated to the Tunnel will be instantiated during registration. This may be seen in logs:

.. code-block :: bash

    cat eophis.out
    # [...]
    -------- Tunnel TO_EARTH registered --------
    # [...]
      Grid demo registered
          Global size: (720, 603)
          Boundary conditions: ('close', 'close')
    ------------------------------------


Assemble a Loop and a Router
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Loop is not a class that can be instantiated but a pre-defined function that emulates time advancement. It takes the time step value and the number of iterations as arguments, and a Tunnel whose methods will be automatically used to orchestrate exchanges in time.

For instance, only one Loop is available in Eophis. It is named ``all_in_all_out`` since it performs all the Tunnel receptions at the beginning of the time step and all the sendings at the end. With the ``earth`` Tunnel defined earlier and the temporal informations obtained in ``earth_namelist``, we can create the Loop as follows:

::

    niter = it_end - it_0 + 1
    @eophis.all_in_all_out(geo_model=earth, step=step, niter=niter)


Router is an empty function that is embedded within the Loop between the reception and the sending phases. Inside the Loop, it receives all the fields obtained during the reception phase and is expected to return all the fields required for the sending back phase. An empty Router assembled with a Loop has the following structure:


::

    @eophis.all_in_all_out(geo_model=earth, step=step, niter=niter)
    def loop_core(**inputs):
        outputs = {}
        # ...
        return outputs

* ``inputs`` is a dictionnary whose keys are the names of all the non-static fields identified as ``in`` in the ``earth`` Tunnel exchanges. Corresponding values are the fields received through the Tunnel.
* ``outputs`` is a dictionnary whose keys must be the names of all the non-static fields identified as ``out`` in the ``earth`` Tunnel exchanges. Values must be the fields to send back through the Tunnel.

In other words, Router delivers all the Tunnel received fields in ``inputs``. User is free to send them towards the imported Models and builds the ``outputs`` content. For the test case of this documentation, the Router is:

::

    @eophis.all_in_all_out(geo_model=earth, step=step, niter=niter)
    def loop_core(**inputs):
        outputs = {}
        outputs['sst_var'] = add_100(inputs['sst'])
        outputs['svt_var'] = add_100(inputs['svt'])
        return outputs

Router content may be more complex but it is recommended to do the extra operations in the imported Models and keep the "y = f(x)" like structure inside the Router.

.. note:: At times that do not match a field frequency, the value in ``inputs`` corresponding to the field name is ``None`` if the field is an ``in`` field. If it is an ``out`` field, the corresponding returned value in ``outputs`` must be ``None``.

    If the Model has been correctly interfaced, those points do not need to be handled.





Preproduction Mode
------------------
At this point, we have a Tunnel that gathers all informations to perform exchanges of coupled fields with "Fake Earth" and a Model with a correct I/O interface. Both are linked with a Router and automated in time with a Loop. The pipeline is ready to be used but we still need to edit the namelists.

::

    eophis.set_mode('preprod')


Edit Namelists
~~~~~~~~~~~~~~

OASIS namcouple
'''''''''''''''
Edit OASIS namelist ``namcouple`` is quite straightforward. During the preproduction mode, register a Tunnel with ``eophis.register_tunnels()`` automatically updates the content of ``namcouple`` that Eophis read at initialization. While not explicitely asked, this updated content only exists in Eophis memory and is not written in files.

In case of a wrong Tunnel registration, it is possible to reset the in-memory ``namcouple`` content with:

::

    eophis.close_tunnels()


A difference is to keep in mind between ``eophis.close_tunnels()`` and ``eophis.init_namcouple()``. The latter reset the content with a new file while the first one reset the content with the same file specified at initialization.

Once all Tunnels have been registered. The command to write the updated OASIS namelist is:

::

    eophis.write_coupling_namelist( simulation_time=total_time )


Total simulation time is required by the OASIS namelist and is passed as argument here from the informations obtained in ``earth_namelist``. If everything went well, a new ``namcouple`` file has been created.

.. code-block :: bash

    cat namcouple
    ############# MODIFIED BY EOPHIS ###############
    $NFIELDS
    5
    $END
    ############
    $RUNTIME
    2424000
    $END
    ############
    $NLOGPRT
    1 0
    $END
    ############
    $STRINGS
    # ======= Tunnel TO_EARTH =======
    # Earth -- sst --> Models
    E_OUT_0 M_IN_0 1 3600 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # Earth <-- sst_var -- Models
    M_OUT_0 E_IN_0 1 3600 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # Earth -- svt --> Models
    E_OUT_1 M_IN_1 1 86400 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # Earth <-- svt_var -- Models
    M_OUT_1 E_IN_1 1 86400 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # ======= Tunnel TO_EARTH_METRIC =======
    # Earth -- msk --> Models
    E_OUT_2 M_IN_2 1 2424000 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    #
    $END

Without going in the details, just note the header that indicates that Eophis worked here and the comments added to identify which sections correspond to which exchanges and Tunnels.

At this point, everything is ready for OASIS. For curious people or OASIS initiated users, a last editing functionality is available. In a ``namcouple`` section, like:

.. code-block :: bash

    # Earth -- sst --> Models
    E_OUT_0 M_IN_0 1 3600 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2

the two first terms are aliases that OASIS uses to perform the communications. ``sst`` is manipulated by OASIS under the name ``E_OUT_0`` from the Fake Earth side and under ``M_IN_0`` from the Python side. Those aliases have been set by default during Tunnel registration.

In Eophis, it does not matter to know these aliases since every OASIS actions are wrapped. On the contrary, it might do from the geoscientific side to setup the coupling, depending on the OASIS implementation.

* A first solution is to check the log file ``eophis.out`` in which aliases are summarized each time a Tunnel is registered.


.. code-block :: bash

    cat eophis.out
    #[...]
    -------- Tunnel TO_EARTH registered --------
      namcouple variable names
        Earth side:
          - sst -> E_OUT_0
          - sst_var -> E_IN_0
          - svt -> E_OUT_1
          - svt_var -> E_IN_1
        Models side:
          - sst -> M_IN_0
          - sst_var -> M_OUT_0
          - svt -> M_IN_1
          - svt_var -> M_OUT_1
    # [...]
    -------- Tunnel TO_EARTH_METRIC registered --------
      namcouple variable names
        Earth side:
          - msk -> E_OUT_2
        Models side:
          - msk -> M_IN_2


* A second solution is to specify user-defined aliases corresponding to those used in the physical code. This can be done with two optional Tunnel arguments ``geo_aliases`` and ``py_aliases``. Both are dictionnaries that associate an alias to the fields names defined in Tunnel for the Earth side and the Model side, respectively. For example:


::
    
    # Configurate a Tunnel for the regular exchanges
    tunnel_config.append( { 'label'      : 'TO_EARTH', \
                            'grids'      : { 'demo' : Domains.demo}, \
                            'exchs'      : [ {'freq' :        3600,  'grd' : 'demo', 'lvl' : 1, 'in' : ['sst'], 'out' : ['sst_var'] },  \
                                             {'freq' : Freqs.DAILY,  'grd' : 'demo', 'lvl' : 3, 'in' : ['svt'], 'out' : ['svt_var'] }], \
                            'geo_aliases' : { 'sst' : 'EAR_SST', 'svt' : 'EAR_TEMP', 'sst_var' : 'EAR_SSTV', 'svt_var' : 'EARTEMPV'},  \
                            'py_aliases'  : { 'sst' : 'EOP_SST', 'svt' : 'EOP_TEMP', 'sst_var' : 'EOP_SSTV', 'svt_var' : 'EOPTEMPV'}   }
                        )

It is of course possible to use only one of these optional arguments and Eophis will complete the missing aliases automatically. After registration and writing, ``namcouple`` content is now:

.. code-block :: bash

    cat namcouple
    ############# MODIFIED BY EOPHIS ###############
    $NFIELDS
    5
    $END
    ############
    $RUNTIME
    2424000
    $END
    ############
    $NLOGPRT
    1 0
    $END
    ############
    $STRINGS
    # ======= Tunnel TO_EARTH =======
    # Earth -- sst --> Models
    EAR_SST EOP_SST 1 3600 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # Earth <-- sst_var -- Models
    EOP_SSTV EAR_SSTV 1 3600 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # Earth -- svt --> Models
    EAR_TEMP EOP_TEMP 1 86400 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # Earth <-- svt_var -- Models
    EOPTEMPV EARTEMPV 1 86400 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    # ======= Tunnel TO_EARTH_METRIC =======
    # Earth -- msk --> Models
    E_OUT_0 M_IN_0 1 2424000 0 rst.nc EXPORTED
    720 603 720 603 demo demo LAG=0
    P 2 P 2
    #
    $END


.. warning :: Eophis never overwrites ``namcouple``. If you made mistakes and want to edit it again, be sure to remove ``namcouple`` if it has the header ``############# MODIFIED BY EOPHIS ###############`` or you will have both the wrong and the corrected contents written in ``namcouple``.


Fortran Namelist
''''''''''''''''
**Planned for next releases**




Production Mode
---------------
At this point, we consider that the coupling material and objects are all well configured. We describe now the functionalities to execute the coupling itself.


::

    eophis.set_mode('prod')

In this mode, Tunnel registration is still required and will check the consistency between ``namcouple`` and the arguments used to define the Tunnels. If the Tunnel and ``namcouple`` content do not match, an error will be raised with details on what was expected and what was read.


Init coupling
~~~~~~~~~~~~~
To initialize the OASIS environement, run:

::

    eophis.open_tunnels()

Coupling is now effective and exchanges may be executed by OASIS and the Tunnels.

.. warning :: To be coupled with OASIS, the Eophis script and the geoscientific code should be launched on the same MPI execution:

    .. code-block :: bash

        mpirun -np 3 python3 ./fake_earth.py : mpirun -np 2 python3 ./main.py

    In this example, ``fake_earth.py`` is running on three processes and ``main.py`` on two.

Calling ``eophis.open_tunnels()`` while Eophis is executed lonely will lead to an error.

To terminate the OASIS environment, use:

::

    eophis.close_tunnels()

.. note:: ``eophis.close_tunnels()`` is automatically called when Eophis execution terminates.



Static Exchanges
~~~~~~~~~~~~~~~~
The sending or the reception of a field defined in an exchange whose frequency is ``Freqs.STATIC`` are done directly with the Tunnel methods. Received and sent fields always have three dimensions corresponding to the local paritioned grid longitude, latitude and depth on which the exchange has been defined, respectively. An error will be raised if sizes do not match.

Static reception of ``msk`` with the Tunnel ``earth_metrics`` is done with:

::

    my_mask = earth_metrics.receive('msk')
    print(my_mask.shape)
    # should print (720,603,1) if executed on one process
    # should print (722,605,1) if defined on a grid with 1 halo, and executed on one process
    
    
This also writes a message in the log file:

.. code-block :: bash

    tail -n 1 eophis.out
    -!- Static receive of msk through tunnel TO_EARTH_METRIC


If ``msk`` would have been defined in an ``out`` exchange, the Tunnel method to send it would have been:
  
::
    
    import numpy as np
    
    # filling my_mask assuming execution on an unique process
    my_mask = np.arange(720*603).reshape(720,603,1)
    earth_metrics.send('msk',my_mask)


Remember that static exchanges can be performed only once and are ignored in Loop. Send or receive a static field already sent or received will be ignored or return ``None`` (``/!\``) with a warning message. Use the above Tunnel methods with fields defined in a non-static exchange will be ignored or return ``None``.

Use a Tunnel with only static exchanges as argument for a Loop will do nothing.

.. note:: A static exchange has no reality for OASIS. The field associated with ``msk`` is sent from the geoscientific side with the OASIS API as any other field. In practice, the frequency value written in ``namcouple`` for a static field is equal to the final simulation time. This way, OASIS allows to perform the exchange only at time zero.



Regular Exchanges
~~~~~~~~~~~~~~~~~
Sending and receiving fields defined in non-static exchanges are automatically done by the Loop. Remember that a Loop won't start if all the static exchanges of all created Tunnels have not been performed before.


::

    eophis.tunnels.ready()

Above function tests if this condition is fulfilled. It is automatically called by the Loop before starting time emulation. Starting a Loop is done with the following command with the Router function as argument:

::

    eophis.starter(loop_core)

Once Loop started, it fills ``eophis.out`` log file with informations about time emulation and realized exchanges. Here are some interesting samples:


.. code-block :: bash

    cat eophis.out
    # [...]
    -------------------- RUN LOOP ----------------------
    Number of iterations : 2000
    Time step : 1200.0s -- 0:20:00
    Total Time : 2400000.0s -- 27 days, 18:40:00

    Modeling routine: ...TO BE COMPLETED...

    Iteration 1: 0s -- 0:00:00
       Treating sst, svt received through tunnel TO_EARTH
       Sending back sst_var, svt_var through tunnel TO_EARTH
    Iteration 4: 3600s -- 1:00:00
       Treating sst received through tunnel TO_EARTH
       Sending back sst_var through tunnel TO_EARTH
    # [...]
    Iteration 1942: 2329200s -- 26 days, 23:00:00
       Treating sst received through tunnel TO_EARTH
       Sending back sst_var through tunnel TO_EARTH
    Iteration 1945: 2332800s -- 27 days, 0:00:00
       Treating sst, svt received through tunnel TO_EARTH
       Sending back sst_var, svt_var through tunnel TO_EARTH
    Iteration 1948: 2336400s -- 27 days, 1:00:00
       Treating sst received through tunnel TO_EARTH
       Sending back sst_var through tunnel TO_EARTH
    # [...]
    Iteration 1996: 2394000s -- 27 days, 17:00:00
       Treating sst received through tunnel TO_EARTH
       Sending back sst_var through tunnel TO_EARTH
    Iteration 1999: 2397600s -- 27 days, 18:00:00
       Treating sst received through tunnel TO_EARTH
       Sending back sst_var through tunnel TO_EARTH
    ------------------- END OF LOOP -------------------

      Closing tunnels

    EOPHIS run finished

Note the beginning of Loop with informations about time emulation and the end with termination messages. Informations are also given about performed exchanges at different moments with ``sst``, ``sst_var``, ``svt`` and ``svt_var`` exchanged with the correct frequencies. At last, iterations at which no exchanges occur are skipped.

Objects
=======

.. autosummary::
   :toctree: generated


Eophis abstractions are presented here. The aim is to explain their roles and functionalities but not to demonstrate how to use them. See usage section with coding examples for this.

Coupling
--------

Tunnel
~~~~~~

The Tunnel represents the gate towards a coupled geoscientific model.

It gathers informations on:
    - global and local grids on which coupled fields are discretized.
    - exchanges themselves, as communication frequencies, corresponding in/out fields names and associated grids.

OASIS objects and commands to execute the sending and reception of fields are encapsulated in the Tunnel.

.. image:: images/eophis_pipeline_1.png
   :width: 700px
   :align: center


.. note:: Tunnel may be summarized with the following thought: **I want to open a gate between my codes to exchange these fields, N times, on this grid**.


Grid
~~~~

The fields sent or received by each coupled scripts are usually scattered among their executing processes.
OASIS needs to know the local grid sizes expressed with global indexes to perform optimized partition-to-partition communications.
If the global sizes are different, OASIS can also perform the interpolation from a grid to another.

.. image:: images/oasis_partitioning.png
    :width: 500px
    :align: center

In the Eophis framework, it is considered that coupled grids are identical on both side. Defining the local partition is still required anyway.
This operation is done by the Grid object. Only global 2D longitude and latitude sizes are required to create a Grid. Third dimension for depth is specified in Tunnel since OASIS considers that sending a 3D field is like communicating N-level times on the same 2D partition.

.. note:: Pre-defined commonly used grids are stored in Eophis sources.


Model
~~~~~

Model refers to the functions in the Python script towards which the exchanged fields should be sent or obtained.

A Model must fit the following requisites:
    - be a callable function that takes at least N numpy arrays as inputs (those are the data received from the Tunnel).
    - return M ``None`` for the M awaited outputs if at least one of the N inputs is ``None``.
    - inputs may be freely formatted and transformed, but outputs must be formatted as numpy arrays whose dimensions correspond to those awaited by the Tunnel grid.


Loop
----

In its standard use, OASIS needs to be aware of the temporal advancement of both coupled scripts to synchronize exchanges in time. In the context of coupling a Python script to use functions (like ML models), time is not computed. Thus, it is needed to mirror the temporal advancement of the coupled geoscientific code to keep synchronicity of exchanges.

Loop is an object that emulates time advancement with a hidden time stepping procedure. It only needs to know the total simulation time and to be associated with a Tunnel.

When Loop starts, all receptions and sendings of the associated Tunnel are temporally orchestrated.

.. Warning:: Time loop won't start if all the Static exchanges (see **Frequency** section) of the associated Tunnel are not done.


Frequency
~~~~~~~~~

Depending on the setup, fields can be exchanged once or repeatedly as the Loop emulates time advancement. Different communication frequencies can be configured for each field.

Two types of frequency are available:
    - Static: sending or receiving a field is done manually ONCE and will be ignored by the Loop. This is useful to obtain non-evolving data as masks or metrics.
    - Non-static: fields will be exchanged at the prescribed frequency (expressed in seconds). Manual sending or receiving are disabled for those fields.

.. Note:: Static frequency is a pre-defined Eophis parameter. Pre-defined regular frequencies are also available.



Router
------

The coupling is now set up with the Tunnel and the exchanges are automated by the Loop. Received fields need then to be sent towards the desired Model inputs and outputed fields need to be pushed in the correct Tunnel for sending back. This pipeline is intended to change with the user wanted realization.

Router is a tool whose role is to offer simplicity and flexibility for setting up connexions between the exchanged data and the inputs / outputs of the Models.

.. image:: images/eophis_pipeline_2.png
   :width: 700px
   :align: center


Miscellaneous
-------------

Above objects are enough to build a basic coupling workflow. Extra useful tools are yet available in the Eophis libary and are presented below.


Namelists
~~~~~~~~~

Geoscientific Fortran / C codes often use namelists to configure the physical context of the simulation. Important informations as time step are stored within.

User is free to hard code the physical context in the Python script. Nevertheless, it is more robust to obtain these informations where the coupled physical code does.

Thus, a tool to read formatted namelist (only Fortran for now) and easily access its content is available in Eophis.

Current implementation does not allow to modify and write a namelist. Update physical namelist in accordance with coupling context could spare user time and errors. This feature is under development for next releases.

.. note:: OASIS namelist *namcouple* is a particular case. Only one OASIS namelist is required for all couplings and needs to be correctly written to avoid errors hard to track. Every action related to Tunnel configuration is supervised by *namcouple*. For all these reasons, object Namcouple is a protected unique entity with its own API.

    It is possible to bring its own *namcouple* and use Eophis to check its content in accordance with the desired coupling context.


Logs
~~~~

Two log files ``eophis.out`` and ``eophis.err`` for regular and warning/error messages are automatically created and filled when importing Eophis package. The API to use them is accessible to the user.

Logs allow three message types:
    - Info: regular outputs in ``eophis.out``
    - Warning: described in ``eophis.err``. Indicates in ``eophis.out`` that a warning occured
    - Abort: Proceed as warning messages, then kill the execution

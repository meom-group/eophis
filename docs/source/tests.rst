Tests
=====

A collection of operating tests for continuous integration and demonstration purposes is provided in the repository. This section describes their purposes and how to use them.


`Write and Couple <https://github.com/meom-group/eophis/tree/main/tests/write_and_couple>`_
-----------------

A surrogate geoscientific code with an OASIS interface is emulated by ``fake_earth.py``.
The script advances in time in accordance with parameters provided in the Fortran namelist ``earth_namelist``.
``models.py`` contains a dummy model ``add_100()`` that we wish to deploy within "Fake Earth". The deployment through OASIS is done with Eophis in ``main.py``.

"Fake Earth" intends to send:
    - one 2D time-evolving field named ``sst`` at a hourly frequency, on grid ``(720,603)``
    - one 3D time-evolving field named ``svt`` at a daily frequency, on grid ``(720,603,3)``
    - one fixed metric field named ``msk`` on the same ``sst`` grid
and to receive from the Python model:
    - one field ``sst_var`` computed from ``sst`` with the same dimensions
    - one field ``svt_var`` computed from ``svt`` with the same dimensions


.. image:: images/write_and_couple_pipeline.png
   :width: 550px
   :align: center


It illustrates :
    - Preproduction and Production modes
    - Tunnel configuration and registration for regular and static exchanges of 2D/3D fields
    - Fortran namelist manipulation
    - Writing of coupling namelist
    - Tunnels opening
    - Assembly of a Loop and a Router
    - Model required global structure
    - Static exchange and start of time emulation for regular exchanges

Following commands run the test (Number of running cpus may be changed in *Makefile*):
    - `make` : execute commands below
    - `make clean` : remove working files
    - `make preprod` : execute eophis in preproduction mode to write coupling namelist
    - `make prod` : execute eophis in production mode for coupling with dummy earth system script


.. code-block:: bash

    cd tests/write_and_couple
    make
    python3 ./main.py --exec preprod
    mv eophis.out preprod_eophis.out
    mpirun -np 1   python3 ./fake_earth.py : -np 1   python3 ./main.py --exec prod
    TEST SUCCESSFUL
    END OF WRITE AND COUPLE TEST
    

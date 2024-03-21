Eophis installation
===================

OASIS with the Python API must be installed first.

OASIS_V5.0
----------

Download OASIS
~~~~~~~~~~~~~~

- Get OASIS sources by cloning git repository:

  .. code-block:: bash

     git clone https://gitlab.com/cerfacs/oasis3-mct.git

  This command may also be found on `CERFACS website <https://oasis.cerfacs.fr/en/>`_.

- Be sure to be on the right commit (``git checkout OASIS3-MCT_5.0``) and go in compilation directory:

  .. code-block:: bash

     cd oasis3-mct/util/make_dir

Compile Libraries
~~~~~~~~~~~~~~~~~

- OASIS libraries must be dynamically compiled to use C and Python APIs. Create and adapt your own "make.<YOUR_ARCH>" file.

- Define the following flags to ensure dynamic compilation:

  .. code-block:: makefile

     DYNOPT = -fPIC
     LDDYNOPT = -shared ${NETCDF_LIBRARY}

  Do not forget to add an include path to the `cbindings` module directory.

- Run Makefile:

  .. code-block:: bash

     make -f TopMakefileOasis3 pyoasis

- If everything goes right, you should find the following libraries in ``oasis3-mct/<YOUR_BLD_DIR>/lib/``:

  - libmct.so
  - libmpeu.so
  - liboasis.cbind.so
  - libpsmile.MPI1.so
  - libscrip.so

PyOASIS
-------

Required Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Source the following files to initialize the PyOASIS modules. The best is to put those commands in your ``.bash_profile``:

  .. code-block:: bash

     source /PATH/TO/oasis3-mct/BLD/python/init.sh
     source /PATH/TO/oasis3-mct/BLD/python/init.csh

- Some python packages are required to use PyOASIS. Use your favorite python environment manager to install and load them:

  - mpi4py
  - numpy
  - netcdf4

- Those are not compulsory but useful to run the tests:

  - matplotlib
  - scipy
  - shapely
  - cartopy
  - pytest

  **NB:** A conda environment file `pyoasis.yml` is provided in the repository.

Testing
~~~~~~~

- Go in directory ``../oasis3-mct/pyoasis/tests`` and execute ``run_pytest.sh`` or directly type ``pytest`` command to run PyOASIS unit tests.

- If successful, go in ``../oasis3-mct/pyoasis/`` and type ``make test`` to execute the OASIS Fortran, C and Python operating tests.

Eophis Package
--------------

- Clone a copy of the repository to your local machine.

  .. code-block:: bash

     git clone https://github.com/alexis-barge/eophis.git
     cd eophis

- Install Eophis package with pip:

  .. code-block:: bash

     pip install eophis

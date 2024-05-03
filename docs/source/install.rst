Eophis installation
===================

.. toctree::
   :maxdepth: 2

OASIS with its Python API must be installed first. More informations may be found on `CERFACS website <https://oasis.cerfacs.fr/en/>`_.

`Prerequisites:`
   - Fortran / C compilers
   - Python environment
   - ``netcdf`` library

OASIS_V5.0
----------


Download OASIS
~~~~~~~~~~~~~~

- Get OASIS sources by cloning git repository:

  .. code-block:: bash

     git clone https://gitlab.com/cerfacs/oasis3-mct.git
     cd oasis3-mct

- Check commit and go in compilation directory:

  .. code-block:: bash

     git checkout OASIS-MCT_5.0
     cd util/make_dir


Compile Libraries
~~~~~~~~~~~~~~~~~

- OASIS libraries must be dynamically compiled. Edit your own ``make.<YOUR_ARCH>`` file.


- Be sure to have the following flags defined for dynamic compilation:

  .. code-block:: makefile

     DYNOPT = -fPIC
     LDDYNOPT = -shared -lnetcdff -lnetcdf


  **NB:** Arch files for common used HPC centers are provided in `repository <https://github.com/meom-group/eophis/tree/main/docs/machine/arch>`_.
  Do not forget to edit ``COUPLE = /PATH/TO/oasis-mct3``.


- Edit ``make.inc`` by adding:

  .. code-block:: bash

     include $(YOUR_OASIS_HOME)/oasis3-mct/util/make_dir/make.<YOUR_ARCH>


- Run Makefile:

  .. code-block:: bash

     make -f TopMakefileOasis3 pyoasis

- If everything goes right, you should find the following libraries in ``oasis3-mct/BLD/lib/``:

  - libmct.so
  - libmpeu.so
  - liboasis.cbind.so
  - libpsmile.MPI1.so
  - libscrip.so

PyOASIS
-------

Required Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Source the following files to initialize PyOASIS modules. The best is to put those commands in your ``.bash_profile``:

  .. code-block:: bash

     source /PATH/TO/oasis3-mct/BLD/python/init.sh
     source /PATH/TO/oasis3-mct/BLD/python/init.csh

- Some python packages are required to use PyOASIS:

  - mpi4py
  - numpy
  - netcdf4

- Those are not compulsory but useful to run the tests:

  - matplotlib
  - scipy
  - shapely
  - cartopy
  - pytest

  **NB:** A conda environment file ``pyoasis.yml`` is provided in `repository <https://github.com/meom-group/eophis/tree/main/docs/machine/envs>`_ for the tests.

Testing
~~~~~~~

- Go in directory ``../oasis3-mct/pyoasis/tests`` and type ``pytest`` command to run unit tests.

- If successful, go in ``../oasis3-mct/pyoasis/`` and type ``make test`` to execute Fortran, C and Python operating tests.



Eophis
------

Package
~~~~~~~

- Check or use the conda environment file ``eophis.yml`` provided in `repository <https://github.com/meom-group/eophis/tree/main/docs/machine/envs>`_ to install the required python packages.


- Clone a copy of the Eophis repository to your local machine.

  .. code-block:: bash

     git clone https://github.com/meom-group/eophis.git


- Install Eophis with pip:

  .. code-block:: bash

     cd eophis
     pip install .

Testing
~~~~~~~

- Run unit tests:

**...WORK IN PROGRESS...**

- Checkout **Tests** section of this documentation to run operating tests.


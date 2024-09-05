Eophis installation
===================

.. toctree::
   :maxdepth: 2

OASIS with its Python API must be installed first. More informations may be found on `CERFACS website <https://oasis.cerfacs.fr/en/>`_.

Prerequisites:
   - Fortran / C compilers
   - `netcdf <https://www.unidata.ucar.edu/software/netcdf/>`_ library for Fortran (>=4.5.2) and C (>=4.7.2)
   - Python environment


OASIS3-MCT_5.0
--------------

Download OASIS
~~~~~~~~~~~~~~

Get OASIS sources by cloning git repository:

.. code-block:: bash

     git clone https://gitlab.com/cerfacs/oasis3-mct.git
     cd oasis3-mct

Check commit and go in compilation directory:

.. code-block:: bash

     git checkout OASIS3-MCT_5.0
     cd util/make_dir


Compile Libraries
~~~~~~~~~~~~~~~~~

OASIS libraries must be dynamically compiled. Edit your own ``make.<YOUR_ARCH>`` file. Be sure to have the following flags defined for dynamic compilation:

.. code-block:: makefile

     DYNOPT = -fPIC
     LDDYNOPT = -shared -lnetcdff -lnetcdf


.. code-block:: bash
    
    # Link your architecture file for compilation
    echo "include ~/oasis3-mct/util/make_dir/make.<YOUR_MACHINE>"  >  make.inc
     
    # Compile dynamic libraries
    make -f TopMakefileOasis3 pyoasis


.. note:: Arch files for common machines and/or HPC centers are provided in OASIS sources.


If everything goes right, you should find the following libraries in ``oasis3-mct/BLD/lib/``:

.. code-block :: bash
    
        ls ~/oasis3-mct/BLD/lib/
        libmct.so   libmpeu.so   liboasis.cbind.so   libpsmile.MPI1.so   libscrip.so

PyOASIS
~~~~~~~

PyOASIS is the Python API of OASIS. Source the following files to initialize PyOASIS modules. The best is to put those commands in your ``.bash_profile``:

.. code-block:: bash

    source /PATH/TO/oasis3-mct/BLD/python/init.sh
    source /PATH/TO/oasis3-mct/BLD/python/init.csh

Python libraries required to use PyOASIS will be automatically installed with Eophis package. For more details, please check out `OASIS documentation <https://oasis.cerfacs.fr/en/documentation/>`_.


Eophis
------

Install package
~~~~~~~~~~~~~~~

Clone a copy of the Eophis repository to your local machine.

.. code-block:: bash

    git clone https://github.com/meom-group/eophis.git


Install Eophis with pip:

.. code-block:: bash

    cd ~/eophis
    pip install .


Testing
~~~~~~~

Running the tests is not mandatory but highly recommended to ensure the proper installation of Eophis. Proceed as follows:


.. code-block:: bash

    # Run operating tests
    cd ~/eophis/tests/
    ./run_all_tests.sh
    # Should print "TEST SUCCESSFUL" for each test

Checkout **Tests** section of this documentation for more informations about operating tests.


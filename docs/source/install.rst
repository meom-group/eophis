Eophis Installation
===================

.. toctree::
   :maxdepth: 2



Eophis can be installed in multiple ways. We recommand installation **From Container** for newcomers or quickstart. Advanced users could follow **From Sources** section for a native build of Eophis.



From Container
--------------

We provide `Apptainer <https://apptainer.org/>`_ (formerly Singularity) images which contain all dependencies and ready-to-use Eophis environment. Follow instructions below to install Apptainer and run containers.


**Apptainer on Linux**

.. code-block :: bash
    
    # For Ubuntu
    sudo apt update && sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:apptainer/ppa
    sudo apt update && sudo apt install -y apptainer
    
    # For amd64 Debian
    sudo apt update
    sudo apt install -y wget
    cd /tmp
    wget https://github.com/apptainer/apptainer/releases/download/v1.4.3/apptainer_1.4.3_amd64.deb
    sudo apt install -y ./apptainer_1.4.3_amd64.deb
    
.. warning :: For other Linux distributions, please refer to this `guide <https://github.com/apptainer/apptainer/blob/main/INSTALL.md>`_.
 

**Apptainer on macOS**

.. code-block:: bash
    
    # Apptainer is available on macOS via LIMA (LInux virtual MAchines)
    brew install qemu lima  # Install with brew
    port install qemu lima  # Install with macports

    # Create Linux VM with Apptainer
    limactl start template://apptainer
    limactl shell apptainer
    # IMPORTANT: type 'cd' to go in VM home, 'pwd' should return '/home/<your_name>.linux'
    cd
    


**Run Eophis containers**

Once you installed Apptainer, or are running the Virtual Machine, you can download and run Eophis containers with:

.. code-block:: bash

    # Get your hardware architecture
    uname -m
    #  aarch64 --> arm64
    #  x86_64  --> amd64

    # For Eophis version 1.0.2 on AMD64 architecture
    export   VER=1.0.2   ARCH=amd64
    wget https://github.com/meom-group/eophis/releases/download/v${VER}/eophis_v${VER}_${ARCH}.zip
    tar -xf eophis_v${VER}_${ARCH}.zip
    # or
    unzip eophis_v${VER}_${ARCH}.zip

    # Run apptainer image
    apptainer run --writable-tmpfs --bind $(pwd):/home/jdoe/to_host eophis_v${VER}_${ARCH}.sif
    
    # In the container: Test Eophis
    cd ~/eophis/tests
    ./run_all_tests.sh
    



From Sources
------------

As a Python package, installing Eophis is straightforward. However, some dependencies are low-level libraries that need to be compiled beforehand. Below, we summarize the steps to build these dependencies.

Please make sure that the following requisites are installed on your system:
   - Fortran / C compilers
   - MPI implementation, such as `OpenMPI <https://www.open-mpi.org/>`_
   - `netcdf <https://www.unidata.ucar.edu/software/netcdf/>`_ library for Fortran (>=4.5.2) and C (>=4.7.2)
   - Python environment (>=3.10)


OASIS3-MCT_5.0
''''''''''''''

**Download and compile OASIS**


Get OASIS sources by cloning git repository:

.. code-block:: bash

     git clone https://gitlab.com/cerfacs/oasis3-mct.git
     cd oasis3-mct

Check commit and go in compilation directory:

.. code-block:: bash

     git checkout OASIS3-MCT_5.0
     cd util/make_dir


OASIS libraries must be dynamically compiled. Edit your own ``make.<YOUR_ARCH>`` file. Pay attention to the following important variables:

.. code-block:: makefile

     # Path for oasis main directory
     COUPLE = /PATH/TO/oasis3-mct
     # Dynamic flags
     DYNOPT = -fPIC
     LDDYNOPT = -shared
     # inc and lib dir
     NETCDF_INCLUDE = /PATH/TO/NETCDF/include
     NETCDF_LIBRARY = -L/PATH/TO/NETCDF/lib -lnetcdf -lnetcdff
     MPI_INCLUDE = /PATH/TO/MPI/include
     MPILIB = -L/PATH/TO/MPI/lib -lmpi
     # Compilers and linker
     F90 = # mpifort -I$(MPI_INCLUDE) , ftn , mpiifort ...
     CC =  # mpicc , cc , mpiicc ...
     LD = $(F90) $(MPILIB)
     # Compilation flags - adapt with your compilers
     FCBASEFLAGS = -O2 ...
     CCBASEFLAGD = -O2 ...

.. note:: Arch files for common machines and/or HPC centers are provided in OASIS sources.


.. code-block:: bash
    
    # Link your architecture file for compilation
    echo "include ~/oasis3-mct/util/make_dir/make.<YOUR_MACHINE>"  >  make.inc
     
    # Compile dynamic libraries
    make -f TopMakefileOasis3 pyoasis



If everything goes right, you should find the following libraries in ``oasis3-mct/BLD/lib/``:

.. code-block :: bash
    
        ls ~/oasis3-mct/BLD/lib/
        libmct.so   libmpeu.so   liboasis.cbind.so   libpsmile.MPI1.so   libscrip.so


**PyOASIS**

PyOASIS is the Python API of OASIS. Source the following files to initialize PyOASIS modules. The best is to put those commands in your ``.bash_profile``:

.. code-block:: bash

    source /PATH/TO/oasis3-mct/BLD/python/init.sh
    source /PATH/TO/oasis3-mct/BLD/python/init.csh

Python libraries required to use PyOASIS will be automatically installed with Eophis package. For more details, please check out `OASIS documentation <https://oasis.cerfacs.fr/en/documentation/>`_.



Eophis
''''''

**Install package**


Clone a copy of the Eophis repository to your local machine.

.. code-block:: bash

    git clone https://github.com/meom-group/eophis.git


Install Eophis with pip:

.. code-block:: bash

    cd ~/eophis
    pip install .


**Testing**

Running the tests is not mandatory but highly recommended to ensure the proper installation of Eophis. Proceed as follows:

.. code-block:: bash

    # Run operating tests
    cd ~/eophis/tests/
    ./run_all_tests.sh
    # Should print "TEST SUCCESSFUL" for each test

Checkout **Tests** section of this documentation for more informations about operating tests.


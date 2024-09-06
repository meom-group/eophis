Eophis
======

.. toctree::
    :maxdepth: 0
    
**Eophis** is a collection of tools that eases the deployment of Python scripts (as pre-trained Machine Learning components) within Fortran/C geoscientific models through OASIS.

    *Also it is the currently oldest known snake ancestra (2023)*

Eophis source code, related files and documentation are distributed under an `MIT License which can be viewed here <https://eophis.readthedocs.io/en/latest/license.html>`_.


Strategy
--------

`OASIS <https://oasis.cerfacs.fr/en/>`_ is a parallelized Fortran coupling library that performs field exchanges between coupled executables. Last releases provided C and Python APIs, which enable coupling between non-homogeneously written codes.

Basically, Eophis allows to:
   (i) wrap an OASIS interface to exchange data with a coupled physic-based code
   (ii) wrap inference models into a simple in/out interface
   (iii) emulate time evolution to synchronize connexions between scripts.


Demonstration Cases
-------------------

Here is a list of repositories containing realizations of coupled runs between different geophysical models and ML models deployed by Eophis:
    
    - `Morays <https://github.com/morays-community>`_ : coupled experiments with ocean codes

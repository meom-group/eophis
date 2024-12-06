Eophis
======

.. toctree::
    :maxdepth: 0
    
**Eophis** is a collection of tools that eases the deployment of Python scripts (such as pre-trained Machine Learning components) within Fortran/C geoscientific models through OASIS. Context of Eophis development is described `here <https://eophis.readthedocs.io/en/latest/concept_motivation.html>`_.

    *Also it is the currently oldest known snake ancestra (2023)*

Eophis source code, related files and documentation are distributed under an `MIT License which can be viewed here <https://eophis.readthedocs.io/en/latest/license.html>`_.

-------------------------------

`OASIS <https://oasis.cerfacs.fr/en/>`_ is a parallelized Fortran coupling library that performs field exchanges between coupled executables. Last releases provided C and Python APIs, which enable coupling between non-homogeneously written codes.


Basically, Eophis allows to:
   (i) wrap an OASIS interface to exchange data with a coupled physic-based code
   (ii) wrap inference models into a simple in/out interface
   (iii) emulate time evolution to synchronize connexions between scripts.

-------------------------------


.. note ::

    Newcomers are welcome to start with:
        - `Eophis tutorial <https://eophis.readthedocs.io/en/latest/tutorial.html>`_
        - `Eophis concepts description <https://eophis.readthedocs.io/en/latest/concept_object.html>`_
        - `Quickstart from container <https://eophis.readthedocs.io/en/latest/install.html#from-container>`_

    People familiar with Eophis may find useful informations in these sections:
        - `Eophis detailed usage <https://eophis.readthedocs.io/en/latest/usage.html>`_
        - `Eophis native installation <https://eophis.readthedocs.io/en/latest/install.html#from-sources>`_

    Advanced users can get inspired by visiting project pages that are using Eophis:
        - Python scripts deployed in ocean models with Eophis : `Morays <https://github.com/morays-community>`_

    People who wish to contribute to Eophis are invited to read:
        - `Contribution guidelines <https://github.com/meom-group/eophis/blob/main/CONTRIBUTING.md>`_
        - `Eophis test suite <https://eophis.readthedocs.io/en/latest/tests.html>`_

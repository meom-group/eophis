"""
domain subpackage
-----------------
Domain refers to the global grid on which the coupling fields are defined.
This subpackage helps to manipulate the grid and decompose it into several subdomains among the executing processes.

The local grid representing the subdomain is divided in two parts:
    - "real cells": cells contained by the subdomain
    - "halo cells": potential external extra cells containing neighbouring subdomains values.

Each subdomain may be translated into two OASIS partition format. One without halos for the sending (Box Partition) and one  with halos for the receiving (Orange Partition).

Tools to generate sending arrays and reshape received arrays with right format are also contained in this subpackage.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""
# package export
from .grid import *
from .halo import *
from .cyclichalo import *
from .nfhalo import *
from .offsiz import *

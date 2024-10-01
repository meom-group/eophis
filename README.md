# Eophis

![Python Version](https://img.shields.io/badge/Python-3.10-blue)
[![C, Fortran, and MPI Required](https://img.shields.io/badge/Compiler-C%20%2F%20Fortran%20%2F%20MPI-important)](https://www.open-mpi.org/)
[![netcdf Required](https://img.shields.io/badge/Build-netCDF%E2%80%93C%20%2F%20netCDF%E2%80%93F-important)](https://www.unidata.ucar.edu/software/netcdf/)
[![Documentation Status](https://readthedocs.org/projects/eophis/badge/?version=latest)](https://eophis.readthedocs.io/en/latest/?badge=latest)


**_Eophis_** is a collection of tools to ease the deployment of Python scripts (as pre-trained Machine Learning components) within Fortran/C geoscientific models through OASIS.
> _Also it is the currently oldest known snake ancestra (2023)_

**Strategy**

[OASIS](https://oasis.cerfacs.fr/en/) is a parallelized Fortran coupling library that performs field exchanges between coupled executables. Last releases provided C and Python APIs, which enable coupling between non-homogeneously written codes. 
Basically, Eophis allows to: 
   - (i) wrap an OASIS interface to exchange data with a coupled physic-based code
   - (ii) wrap inference models into a simple in/out interface
   - (iii) emulate time evolution to synchronize connexions between scripts.

**Current development objectives**
   - tools to write coupling info in geoscientific codes namelists
   - tools for time diagnostic
   - enhance packaging
   - add more detailed tutorial

## Usage, installation and test cases

Check out corresponding sections in [Eophis documentation](https://eophis.readthedocs.io/en/latest/index.html) for further informations.

## Demonstration cases

Those projects use Eophis:
- [Morays](https://github.com/morays-community) : Python scripts deployed in ocean models with Eophis


## How to cite

[![DOI](https://zenodo.org/badge/713480336.svg)](https://doi.org/10.5281/zenodo.13852038) 

Please use above DOI or **Cite this repository** button in the **About** section of the repository


## License

Copyright &copy; IGE-MEOM

Eophis is distributed under the [MIT License](https://github.com/meom-group/eophis/blob/main/LICENSE).

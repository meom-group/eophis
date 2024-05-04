# Eophis

**_Eophis_** is a collection of tools to ease the deployment of Python scripts (as pre-trained Machine Learning components) within Fortran/C geoscientific models through OASIS.
> _Also it is the currently oldest known snake ancestra (2023)_

**Strategy**

[OASIS](https://oasis.cerfacs.fr/en/) is a parallelized Fortran coupling library that performs field exchanges between coupled executables. Last releases provided C and Python APIs, which enable coupling between non-homogeneously written codes. 
Basically, Eophis allows to: 
   - (i) wrap an OASIS interface to exchange data with a coupled physic-based code
   - (ii) wrap inference models into a simple in/out interface
   - (iii) emulate time evolution to synchronize connexions between scripts.

**Current development objectives**
   - automatic creation of grid halos during parallel execution
   - support GPU computing
   - tools to write coupling info in geoscientific codes namelists

## Usage, installation and test cases

Check out corresponding sections in [Eophis documentation](https://eophis.readthedocs.io/en/latest/index.html) for further informations.


## Demonstration cases

Here is a list of repositories containing realizations of coupled runs between different geophysical models and ML models deployed by Eophis:
- [Morays](https://github.com/morays-community) : coupled runs with ocean codes


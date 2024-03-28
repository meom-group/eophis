# Eophis

Eophis is a collection of tools to deploy Python written pre-trained Machine Learning components (Inference Models) within Fortran/C/Python written Earth-System (ES) models via OASIS.
> _Also it is the currently oldest known snake ancestra (2023)_

**Strategy**

[OASIS](https://oasis.cerfacs.fr/en/) is a Fortran coupling library that performs field exchanges between coupled executables. Last releases provided C and Python APIs, which enable coupling between non-homogeneously written codes. 
Basically, Eophis allows to: 
   - (i) wrap an OASIS interface to exchange data with a coupled ES code
   - (ii) wrap inference models into a simple in/out interface
   - (iii) emulate time evolution to synchronize connexions between ES and models.

**Current development objectives**
   - write unit tests and testing routines
   - write detailed documentation
   - automatic creation of grid halos during parallel execution
   - support GPU computing
   - tools to write coupling info in ES namelists

## Usage and installation

Check out [Eophis documentation](https://eophis.readthedocs.io/en/latest/index.html) for further informations.


## Demonstration cases

Here is a list of repositories containing realizations of coupled runs between different ES models and inferences models deployed by Eophis:
- [Morays](https://github.com/morays-community) : coupled runs with ocean codes


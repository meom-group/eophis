# Eophis

**E**... **O**... **P**... **H**... **I**... **S**...

Eophis is a collection of tools to deploy Python written pre-trained Machine Learning components (Inference Models) within Fortran/C/Python written Earth-System (ES) models via OASIS.
> _Also it is the currently oldest known snake ancestra (2023)_

## Overview

**Strategy**

[OASIS](https://oasis.cerfacs.fr/en/) is a Fortran coupling library that performs field exchanges between coupled executables. Last releases provided C and Python APIs, which enable coupling between non-homogeneously written codes. Basically, Eophis allows to: (i) wrap an OASIS interface to exchange data with a coupled ES code, (ii) wrap inference models into a simple in/out interface, and (iii) emulate time evolution to synchronize connexions between ES and models.

**Current development objectives**
   - write unit tests and testing routines
   - write detailed documentation
   - automatic creation of grid halos during parallel execution
   - support GPU computing
   - tools to write coupling info in ES namelists

## Repository Content

### docs 

Detailed documentation about installation and use of Eophis. 
- Quick [guide](https://github.com/alexis-barge/eophis/blob/main/docs/pyOASIS_installation.md) to manually install OASIS libraries with python API (compulsory).
- ...

### tests 
- Unit tests
- Operating examples


### src
Package sources: 
- _namcoupe_eophis_ : default OASIS namelist for coupling instruction
- **coupling :** ES and OASIS namelists manipulation tools, coupling environment manager
- **inference :** models wrappers (empty for now)
- **loop :** time emulators
- **utils :** operating tools


## Package Installation

**Warning: Eophis is currently a development version and may contain bugs and limited functionalities.**

- Clone a copy of the repository to your local machine.
```bash
git clone https://github.com/alexis-barge/eophis.git 
cd eophis
```
- Install Eophis package with pip :
```bash
pip install eophis
```
- Be sure to have OASIS installed on your local machine beforehand to use Eophis package (see docs).

## Demonstration cases

Here is a list of repositories containing realizations of coupled runs between different ES models and inferences models deployed by Eophis:
- [Morays](https://github.com/alexis-barge/morays/) : coupled runs with ocean modelling code [NEMO](https://www.nemo-ocean.eu/) 


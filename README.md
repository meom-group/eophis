# Eophis

**<span style="color:red">E</span>... <span style="color:red">O</span>... <span style="color:red">P</span>... <span style="color:red">H</span>... <span style="color:red">I</span> ... <span style="color:red">S</span>...**

Eophis is a collection of tools to deploy Python written pre-trained machine learning components (Inference Models) for coupled runs with Fortran written Earth-System (ES) simulations.
> _Also it is the currently oldest known snake ancestra (2023)_

## Overview

**Strategy**

[OASIS](https://oasis.cerfacs.fr/en/) is a Fortran coupling library that performs field exchanges between two coupled executables. Last release provided C and Python APIs, which enables coupling between non-homogeneously written codes. Basically, Eophis does: (i) wrapp an OASIS interface to exchange data with ES, (ii) wrapp inference models into a simple in/out interface, and (iii) emulates time evolution to synchronize connexions between ES and models.

**Short term development objectives**
   - debug and assess beta version
   - write unit tests and testing routine
   - write detailed documentation
   - optimize parallel data management

**Long term development objectives:**
   - keep the architecture generic enough to be used by the different climate science and machine learning communities.

## Repository Content

### docs 

Detailed documentation about installation and use of Eophis. 
- Quick [guide](https://github.com/alexis-barge/eophis/blob/main/python_cpl/pyOASIS_installation.md) to manually install OASIS libraries with python API (compulsory).
- ...

### tests 
Unit tests and testing routines. 
<span style="color:red">Work In Progress</span>

### src
Package sources: 
- _namcoupe_base_ : default OASIS namelist for coupling instruction
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

## Examples

Here is a list of repositories containing demonstrations of coupled runs between different ES codes and inferences models deployed by Eophis:
- [Morays](https://github.com/alexis-barge/morays/) : coupled runs with ocean modelling code [NEMO](https://www.nemo-ocean.eu/) 
- ...


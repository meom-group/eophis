# Tests

Collection of tests for continuous integration.

## Unit Tests

...WORK IN PROGRESS...

## Operating Examples

### write and couple

Illustrates :
- Preproduction and Production modes
- Tunnel configuration and registration for regular and static exchanges of 2D/3D fields
- Fortran namelist manipulation
- Writing of coupling namelist
- Tunnels opening
- Assembly of an All In All Out time loop with the fields-to-models connexions
- Inference Model required global structure
- Static exchange and start of time emulation for regular exchanges

Following commands run the test (Number of running cpus may be changed in _Makefile_):
- `make` : execute commands below 
- `make clean` : remove working files
- `make preprod` : execute eophis in preproduction mode to write coupling namelist
- `make prod` : execute eophis in production mode for coupling with dummy earth system script

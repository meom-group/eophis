#!/bin/bash
n1=1  ## number of process for toy earth script
n2=1  ## number of process for eophis script

default: clean preprod prod
	@echo 'END OF HALOS DECOMPOSITION TEST'

# create coupling namelist
preprod:
	python3 ./main.py --exec preprod
	mv eophis.out preprod_eophis.out

# run coupled test
prod:
	mpirun -np $(n1) python3 ./tpy_earth.py : -np $(n2) python3 ./main.py --exec prod

# remove working file
clean:
	@-rm namcouple* nout* debug* *.log *.out *.err

# purge
veryclean: clean
	@-rm -r __pycache__

#!/bin/bash
n1=1  ## number of processor for fake earth script
n2=1  ## number of processors for eophis script

default: clean preprod prod
	@echo 'END OF WRITE AND COUPLE TEST'

# create coupling namelist
preprod:
	python3 ./main.py --exec preprod
	mv eophis.out preprod_eophis.out

# run coupled test
prod:
	mpirun -np $(n1) python3 ./fake_earth.py : -np $(n2) python3 ./main.py --exec prod

# remove working file
clean:
	-rm namcouple* nout* debug* *.log *.out *.err

# purge
veryclean: clean
	-rm -r __pycache__

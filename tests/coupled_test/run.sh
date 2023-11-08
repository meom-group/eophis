#!/bin/bash

## purge
rm namcouple* nout* debug* *.log *.out *.err

## create namelist
python3 ./main.py --exec preprod
mv eophis.out preprod_eophis.out

## coupled run
n1=1
n2=1
mpirun -np $n1 python3 ./main.py --exec prod : -np $n2 python3 ./fake_earth.py

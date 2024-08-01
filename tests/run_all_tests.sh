#!/bin/bash
TESTDIR=$(pwd)

# write_and_couple
echo 'RUN WRITE AND COUPLE TEST'
cd ${TESTDIR}/write_and_couple/
make
make veryclean

# halo decomposition
echo 'RUN HALO DECOMPOSITION TEST'
cd ${TESTDIR}/halo_decomposition/
make
make veryclean

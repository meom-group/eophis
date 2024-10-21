#!/bin/bash
TESTDIR=$(pwd)

# write_and_couple
echo ''
echo '-------------------------'
echo 'RUN WRITE AND COUPLE TEST'
echo '-------------------------'
cd ${TESTDIR}/write_and_couple/
make
if grep -q "TEST FAILED" earth.log; then
  exit 1
fi
make veryclean


# halo decomposition
echo ''
echo '---------------------------'
echo 'RUN HALO DECOMPOSITION TEST'
echo '---------------------------'
cd ${TESTDIR}/halo_decomposition/
make
if grep -q "TEST FAILED" earth.log; then
  exit 1
fi
make veryclean

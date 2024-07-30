import os
import shutil
import pytest
import numpy as np
#
import eophis

# ========
# cleaning
# ========
@pytest.fixture(scope="session",autouse=True)
def clean_files():
    yield
    for file_name in ["eophis.out", "eophis.err"]:
        if os.path.exists(file_name):
            os.remove(file_name)
    if os.path.exists("test_namcouple"):
        os.remove("test_namcouple")
    shutil.rmtree("__pycache__")


# ==============
# test nfhalo.py
# ==============
from eophis.domain.nfhalo import NFHalo
from eophis.domain.offsiz import set_fold_trf

# global grid - F grid, F fold point
folds_FF = set_fold_trf('F','F')

# -- cross top bnd
def test_6x4_4x1_F_F_top():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(4,1), offset=1, fold_param=folds_FF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0],[12])
    # rebuild halos
    res = hls.rebuild_halos(np.array([8,9,10,11]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[11,10,9,8]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(12).reshape(12,1,order='F')+1).transpose()
    ref = np.array( [ [[11,10,9,8,7,12],[1,2,3,4,5,6],[7,8,9,10,11,12]] ] )
    assert np.array_equal(ref,res) == True

# -- upper left
def test_6x4_1x1_F_F_upleft():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(1,1), offset=1, fold_param=folds_FF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6],[3,5])
    # rebuild halos
    res = hls.rebuild_halos(np.array([9,10,11]).reshape(3,1,order='F')).transpose()
    ref = np.array( [[[11,10,9]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,7,8,9,10,11])
    res = hls.rebuild(grid.reshape(8,1,order='F')).transpose()
    ref = np.array( [ [[11,10,9],[1,2,3],[7,8,9]] ] )
    assert np.array_equal(ref,res) == True

# -- upper right
def test_6x4_1x1_F_F_upright():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,1), offset=11, fold_param=folds_FF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-2,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,3,9,15,21],[2,5,5,5,3])
    # rebuild halos
    res = hls.rebuild_halos(np.array([8,9,10,11]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[11,10,9,8]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,4,5,6,7,8,10,11,12,13,14,16,17,18,19,20,22,23,24])
    res = hls.rebuild(grid.reshape(20,1,order='F')).transpose()
    ref = np.array( [ [[8,7,12,11,10],[4,5,6,1,2],[10,11,12,7,8],[16,17,18,13,14],[22,23,24,19,20]] ] )
    assert np.array_equal(ref,res) == True

# -- total grid
def test_6x4_6x4_F_F_total():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_FF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[13,18,17,16,15,14,13,18,17,16],[7,12,11,10,9,8,7,12,11,10],[5,6,1,2,3,4,5,6,1,2],[11,12,7,8,9,10,11,12,7,8],[17,18,13,14,15,16,17,18,13,14],[23,24,19,20,21,22,23,24,19,20],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

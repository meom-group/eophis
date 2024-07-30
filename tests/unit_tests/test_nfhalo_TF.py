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

# global grid - T grid, F fold point
folds_TF = set_fold_trf('T','F')

# -- cross top bnd
def test_6x4_1x3_T_F_top():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(1,3), offset=3, fold_param=folds_TF, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([1,8,14,20],[4,3,3,3])
    # rebuild grid
    grid = np.array([2,3,4,5,9,10,11,15,16,17,21,22,23])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[4,3,2],[3,4,5],[9,10,11],[15,16,17],[21,22,23]] ] )
    assert np.array_equal(ref,res) == True

# -- upper left
def test_6x4_1x1_T_F_upleft():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,1), offset=0, fold_param=folds_TF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (2,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,16],[15,2])
    # rebuild grid
    grid = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18])
    res = hls.rebuild(grid.reshape(17,1,order='F')).transpose()
    ref = np.array( [ [[8,7,12,11,10],[2,1,6,5,4],[5,6,1,2,3],[11,12,7,8,9],[17,18,13,14,15]] ] )
    assert np.array_equal(ref,res) == True

# -- upper right
def test_6x4_1x1_T_F_upright():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,1), offset=5, fold_param=folds_TF, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-2,2)
    assert hls.close == -2
    # segment
    res = hls.segment()
    assert res == ([0,15],[14,3])
    # rebuild grid
    grid = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18])
    res = hls.rebuild(grid.reshape(17,1,order='F')).transpose()
    ref = np.array( [ [[9,8,7,0,0],[3,2,1,0,0],[4,5,6,0,0],[10,11,12,0,0],[16,17,18,0,0]] ] )
    assert np.array_equal(ref,res) == True
    
# -- top line
def test_6x4_6x2_T_F_tline():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,2), offset=0, fold_param=folds_TF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0],[18])
    # rebuild grid
    res = hls.rebuild(np.arange(18).reshape(18,1,order='F')+1).transpose()
    ref = np.array( [ [[1,6,5,4,3,2,1,6],[6,1,2,3,4,5,6,1],[12,7,8,9,10,11,12,7],[18,13,14,15,16,17,18,13]] ] )
    assert np.array_equal(ref,res) == True

# -- left column
def test_6x4_1x4_T_F_lcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=0, fold_param=folds_TF, bnd=('close','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (2,2)
    assert hls.close == 2
    # segment
    res = hls.segment()
    assert res == ([0,16,22],[15,5,2])
    # rebuild grid
    grid = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[0,0,12,11,10],[0,0,6,5,4],[0,0,1,2,3],[0,0,7,8,9],[0,0,13,14,15],[0,0,19,20,21],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- right column
def test_6x4_1x3_T_F_rcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=5, fold_param=folds_TF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-2,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,15,21],[14,5,3])
    # rebuild grid
    grid = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19,20,22,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[9,8,7,12,11],[3,2,1,6,5],[4,5,6,1,2],[10,11,12,7,8],[16,17,18,13,14],[22,23,24,19,20],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- total grid
def test_6x4_6x4_T_F_total():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_TF, bnd=('close','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,1)
    assert hls.close == 1
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[0,6,5,4,3,2,1,0],[0,1,2,3,4,5,6,0],[0,7,8,9,10,11,12,0],[0,13,14,15,16,17,18,0],[0,19,20,21,22,23,24,0],[0,0,0,0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True


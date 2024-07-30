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

# global grid - U grid, T fold point
folds_UT = set_fold_trf('U','T')

# -- cross top bnd
def test_6x4_2x2_U_T_top():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,2), offset=2, fold_param=folds_UT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([1,7,13],[4,4,4])
    # rebuild halos
    res = hls.rebuild_halos(np.array([8,9,10,11]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[11,10,9,8]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([2,3,4,5,8,9,10,11,14,15,16,17])
    res = hls.rebuild(grid.reshape(12,1,order='F')).transpose()
    ref = np.array( [ [[11,10,9,8],[2,3,4,5],[8,9,10,11],[14,15,16,17]] ] )
    assert np.array_equal(ref,res) == True

# -- upper left
def test_6x4_2x2_U_T_upleft():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,2), offset=0, fold_param=folds_UT, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (1,1)
    assert hls.close == 1
    # segment
    res = hls.segment()
    assert res == ([0,5,17],[3,10,1])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,10,11,12]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[7,12,11,10]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,6,7,8,9,10,11,12,13,14,15,18])
    res = hls.rebuild(grid.reshape(14,1,order='F')).transpose()
    ref = np.array( [ [[0,12,11,10],[0,1,2,3],[0,7,8,9],[0,13,14,15]] ] )
    assert np.array_equal(ref,res) == True

# -- upper right
def test_6x4_2x2_U_T_upright():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,2), offset=4, fold_param=folds_UT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-1,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,3,15],[1,10,3])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,9,12]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[9,8,7,12]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([1,4,5,6,7,8,9,10,11,12,13,16,17,18])
    res = hls.rebuild(grid.reshape(14,1,order='F')).transpose()
    ref = np.array( [ [[9,8,7,12],[4,5,6,1],[10,11,12,7],[16,17,18,13]] ] )
    assert np.array_equal(ref,res) == True

# -- top line
def test_6x4_6x1_U_T_tline():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,1), offset=0, fold_param=folds_UT, bnd=('close','nfold') )
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == 1
    # intern segments
    assert hls.segment_intern_fold(9) == ([9,6],[3,3])
    assert hls.segment_intern_fold(14) == ([14,12],[4,2])
    assert hls.segment_intern_fold(11) == ([11,6],[1,5])
    assert hls.segment_intern_fold(6) == ([6],[6])
    # offsets/sizes from rebuild, copies and moves
    res = hls.rebuild_instructions([[0, 6], [6]],[[6, 6], [6]])
    assert res == ([0],[12])
    assert np.array_equal( hls._copies, np.array([[6,12]]) ) == True
    assert np.array_equal( hls._moves, np.array([]) ) == True
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,9,10,11,12]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[12,11,10,9,8,7]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(12).reshape(12,1,order='F')+1).transpose()
    ref = np.array( [ [[0,12,11,10,9,8,7,0],[0,1,2,3,4,5,6,0],[0,7,8,9,10,11,12,0]] ] )
    assert np.array_equal(ref,res) == True

# -- left column
def test_6x4_2x4_U_T_lcol():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,4), offset=0, fold_param=folds_UT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (1,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,5,17,23],[3,10,4,1])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,10,11,12]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[7,12,11,10]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,6,7,8,9,10,11,12,13,14,15,18,19,20,21,24])
    res = hls.rebuild(grid.reshape(18,1,order='F')).transpose()
    ref = np.array( [ [[7,12,11,10],[6,1,2,3],[12,7,8,9],[18,13,14,15],[24,19,20,21],[0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- right column
def test_6x4_1x4_U_T_rcol():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(1,4), offset=5, fold_param=folds_UT, bnd=('close','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-1,1)
    assert hls.close == -1
    # segment
    res = hls.segment()
    assert res == ([0,4,10,16,22],[1,4,3,3,2])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,12]).reshape(3,1,order='F')).transpose()
    ref = np.array( [[[8,7,12]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    grid = np.array([1,5,6,7,8,11,12,13,17,18,19,23,24])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[8,7,0],[5,6,0],[11,12,0],[17,18,0],[23,24,0],[0,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- total grid
def test_6x4_6x4_U_T_total():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_UT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[7,12,11,10,9,8,7,12],[6,1,2,3,4,5,6,1],[12,7,8,9,10,11,12,7],[18,13,14,15,16,17,18,13],[24,19,20,21,22,23,24,19],[0,0,0,0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True


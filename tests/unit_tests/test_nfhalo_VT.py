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
    if os.path.isdir("__pycache__"):
        shutil.rmtree("__pycache__")

# ==============
# test nfhalo.py
# ==============
from eophis.domain.nfhalo import NFHalo
from eophis.domain.offsiz import set_fold_trf

# global grid - V grid, T fold point
folds_VT = set_fold_trf('V','T')

# -- cross top bnd
def test_6x4_2x1_V_T_top():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=8, fold_param=folds_VT, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment, copies, moves
    res = hls.segment()
    assert res == ([0],[24])
    assert np.array_equal( hls._copies, np.array([[12,18]]) ) == True
    assert np.array_equal( hls._moves, np.array([]) ) == True
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[13,18,17,16,15,14]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[13,18,17,16,15,14],[1,2,3,4,5,6],[7,8,9,10,11,12],[13,14,15,16,17,18],[19,20,21,22,23,24]] ] )
    assert np.array_equal(ref,res) == True

# -- upper left
def test_6x4_2x1_V_T_upleft():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=7, fold_param=folds_VT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (1,1)
    assert hls.close == 0
    # segment, copies, moves
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[14,13,18,17,16,15]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[14,13,18,17,16,15],[6,1,2,3,4,5],[12,7,8,9,10,11],[18,13,14,15,16,17],[24,19,20,21,22,23]] ] )
    assert np.array_equal(ref,res) == True

# -- upper right
def test_6x4_2x1_V_T_upright():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=10, fold_param=folds_VT, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-2,1)
    assert hls.close == -2
    # segment, copies, moves
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[17,16,15,14,13,18]]] )
    assert np.array_equal(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[17,16,15,14,0,0],[3,4,5,6,0,0],[9,10,11,12,0,0],[15,16,17,18,0,0],[21,22,23,24,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- top line
def test_6x4_6x1_V_T_tline():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(6,1), offset=6, fold_param=folds_VT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment, copies, moves
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[15,14,13,18,17,16,15,14,13,18],[5,6,1,2,3,4,5,6,1,2],[11,12,7,8,9,10,11,12,7,8],[17,18,13,14,15,16,17,18,13,14],[23,24,19,20,21,22,23,24,19,20]] ] )
    assert np.array_equal(ref,res) == True

# -- left column
def test_6x4_1x4_V_T_lcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=1, fold_param=folds_VT, bnd=('close','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (1,2)
    assert hls.close == 1
    # segment, copies, moves
    res = hls.segment()
    assert res == ([0,5,11],[4,5,13])
    # rebuild grid
    grid = np.array([1,2,3,4,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[0,19,24,23,22],[0,13,18,17,16],[0,1,2,3,4],[0,7,8,9,10],[0,13,14,15,16],[0,19,20,21,22],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- right column
def test_6x4_1x4_V_T_rcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=4, fold_param=folds_VT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-1,2)
    assert hls.close == 0
    # segment, copies, moves
    res = hls.segment()
    assert res == ([0,2,8],[1,5,16])
    # rebuild grid
    grid = np.array([1,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[23,22,21,20,19],[17,16,15,14,13],[3,4,5,6,1],[9,10,11,12,7],[15,16,17,18,13],[21,22,23,24,19],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

# -- total grid
def test_6x4_6x4_V_T_total():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_VT, bnd=('close','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,2)
    assert hls.close == 2
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,19,24,23,22,21,20,0,0],[0,0,13,18,17,16,15,14,0,0],[0,0,1,2,3,4,5,6,0,0],[0,0,7,8,9,10,11,12,0,0],[0,0,13,14,15,16,17,18,0,0],[0,0,19,20,21,22,23,24,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]] ] )
    assert np.array_equal(ref,res) == True

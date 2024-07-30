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
from eophis.coupling.nfhalo import NFHalo
from eophis.coupling.offsiz import set_fold_trf

# ====================================================================

# global grid - T grid, T fold point
folds_TT = set_fold_trf('T','T')

# -- cross top bnd
def test_6x4_2x2_T_T_top():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,2), offset=2, fold_param=folds_TT, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # intern segments
    assert hls.segment_intern_fold(9) == ([9],[2])
    assert hls.segment_intern_fold(14) == ([14],[2])
    assert hls.segment_intern_fold(11) == ([11,6],[1,1])
    assert hls.segment_intern_fold(6) == ([6],[2])
    # offsets/sizes from rebuild, copies and moves
    res = hls.rebuild_instructions([ [2,1,4,8,7,10,14,13,16], [9,8,11] ], [ [2,1,1,2,1,1,2,1,1], [2,1,1] ])
    assert res == ([1,7,13],[4,5,4])
    assert np.equal_array( hls.copies, np.array([[5,9]]) ) == True
    assert np.equal_array( hls.moves, np.array([[5,9]]) ) == True
    # rebuild halos
    res = hls.rebuild_halos(np.array([9,10,11,12]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[12,11,10,9]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([2,3,4,5,8,9,10,11,12,14,15,16,17])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[12,11,10,9],[2,3,4,5],[8,9,10,11],[14,15,16,17]] ] )
    assert np.equal_array(ref,res) == True

# -- upper left
def test_6x4_2x2_T_T_upleft():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,2), offset=0, fold_param=folds_TT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (1,1)
    assert hls.close == 0
    # offsets/sizes from rebuild, copies and moves
    res = hls.rebuild_instructions([[0,5,2,6,11,8,12,17,14], [11,6,10,7]],[[2,1,1,2,1,1,2,1,1], [1,1,1,1]])
    assert res == ([0,5,10,17],[3,4,5,1])
    assert np.equal_array( hls.copies, np.array([[4,6],[7,9]]) ) == True
    assert np.equal_array( hls.moves, np.array([[7,8]]) ) == True
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,11,12]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[8,7,12,11]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,6,7,8,9,11,12,13,14,15,18])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[8,7,12,11],[6,1,2,3],[12,7,8,9],[18,13,14,15]] ] )
    assert np.equal_array(ref,res) == True

# -- upper right
def test_6x4_2x2_T_T_upright():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,2), offset=4, fold_param=folds_TT, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-1,1)
    assert hls.close == -1
    # segment
    res = hls.segment()
    assert res == ([0,3,15],[1,10,3])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,9,10]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[10,9,8,7]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,4,5,6,7,8,9,10,11,12,13,16,17,18])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[10,9,8,0],[4,5,6,0],[10,11,12,0],[16,17,18,0]] ] )
    assert np.equal_array(ref,res) == True

# -- top line
def test_6x4_6x1_T_T_tline():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,1), offset=0, fold_param=folds_TT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0],[12])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,9,10,11,12]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[7,12,11,10,9,8]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
    res = hls.rebuild(grid.reshape(12,1,order='F')).transpose()
    ref = np.array( [ [[8,712,11,10,9,8,7],[6,1,2,3,4,5,6,1],[12,7,8,9,10,11,12,7]] ] )
    assert np.equal_array(ref,res) == True

# -- left column
def test_6x4_2x4_T_T_lcol():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,4), offset=0, fold_param=folds_TT, bnd=('close','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (1,1)
    assert hls.close == 1
    # segment
    res = hls.segment()
    assert res == ([0,5,10,17,23],[3,4,5,4,1])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,12]).reshape(3,1,order='F')).transpose()
    ref = np.array( [[[8,7,12]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,6,7,8,9,11,12,13,14,15,18,19,20,21,24])
    res = hls.rebuild(grid.reshape(17,1,order='F')).transpose()
    ref = np.array( [ [[0,7,12,11],[0,1,2,3],[0,7,8,9],[0,13,14,15],[0,19,20,21],[0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- right column
def test_6x4_1x4_T_T_rcol():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(1,4), offset=5, fold_param=folds_TT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-1,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,4,10,16,22],[1,5,3,3,2])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,9]).reshape(3,1,order='F')).transpose()
    ref = np.array( [[9,8,7]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,5,6,7,8,9,11,12,13,17,18,19,23,24])
    res = hls.rebuild(grid.reshape(14,1,order='F')).transpose()
    ref = np.array( [ [[9,8,7],[5,6,1],[11,12,7],[17,18,13],[23,24,19],[0,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- total grid
def test_6x4_6x4_T_T_total():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_TT, bnd=('close','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,1)
    assert hls.close == 1
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[0,7,12,11,10,9,8,0],[0,1,2,3,4,5,6,0],[0,7,8,9,10,11,12,0],[0,13,14,15,16,17,18,0],[0,19,20,21,22,23,24,0],[0,0,0,0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True



# ====================================================================

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
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([2,3,4,5,8,9,10,11,14,15,16,17])
    res = hls.rebuild(grid.reshape(12,1,order='F')).transpose()
    ref = np.array( [ [[11,10,9,8],[2,3,4,5],[8,9,10,11],[14,15,16,17]] ] )
    assert np.equal_array(ref,res) == True

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
    ref = np.array( [[7,12,11,10]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,6,7,8,9,10,11,12,13,14,15,18])
    res = hls.rebuild(grid.reshape(14,1,order='F')).transpose()
    ref = np.array( [ [[0,12,11,10],[0,1,2,3],[0,7,8,9],[0,13,14,15]] ] )
    assert np.equal_array(ref,res) == True

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
    ref = np.array( [[]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,4,5,6,7,8,9,10,11,12,13,16,17,18])
    res = hls.rebuild(grid.reshape(14,1,order='F')).transpose()
    ref = np.array( [ [[9,8,7,12],[4,5,6,1],[10,11,12,7],[16,17,18,13]] ] )
    assert np.equal_array(ref,res) == True

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
    res = hls.rebuild_instructions([[0, 6], [6]],[[6, 6], [6]]))
    assert res == ([0],[12])
    assert np.equal_array( hls.copies, np.array([[6,12]]) ) == True
    assert np.equal_array( hls.moves, np.array([]) ) == True
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,8,9,10,11,12]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[12,11,10,9,8,7]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(12).reshape(12,1,order='F')+1).transpose()
    ref = np.array( [ [[0,12,11,10,9,8,7,0],[0,1,2,3,4,5,6,0],[0,7,8,9,10,11,12,0]] ] )
    assert np.equal_array(ref,res) == True

# -- left column
def test_6x4_2x4_U_T_lcol():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(2,4), offset=0, fold_param=folds_UT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (1,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([[0,5,17,23],[3,10,4,1]])
    # rebuild halos
    res = hls.rebuild_halos(np.array([7,10,11,12]).reshape(4,1,order='F')).transpose()
    ref = np.array( [[[7,12,11,10]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,6,7,8,9,10,11,12,13,14,15,18,19,20,21,24])
    res = hls.rebuild(grid.reshape(18,1,order='F')).transpose()
    ref = np.array( [ [[7,12,11,10],[6,1,2,3],[12,7,8,9],[18,13,14,15],[24,19,20,21],[0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,5,6,7,8,11,12,13,17,18,19,23,24])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[8,7,0],[5,6,0],[11,12,0],[17,18,0],[23,24,0],[0,0,0]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True


# ====================================================================

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
    assert np.equal_array( hls.copies, np.array([[12,18]]) ) == True
    assert np.equal_array( hls.moves, np.array([]) ) == True
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18]).reshape(6,1,order='F')).transpose()
    ref = np.array( [[[13,18,17,16,15,14]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[13,18,17,16,15,14],[1,2,3,4,5,6],[7,8,9,10,11,12],[13,14,15,16,17,18],[19,20,21,22,23,24]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[14,13,18,17,16,15],[6,1,2,3,4,5],[12,7,8,9,10,11],[18,13,14,15,16,17],[24,19,20,21,22,23]] ] )
    assert np.equal_array(ref,res) == True

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
    ref = np.array( [[[17,16,15,14,0,0]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[17,16,15,14,0,0],[3,4,5,6,0,0],[9,10,11,12,0,0],[15,16,17,18,0,0],[21,22,23,24,0,0]] ] )
    assert np.equal_array(ref,res) == True

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
    ref = np.array( [ [[15,14,13,18,17,16,15,14,13],[5,6,1,2,3,4,5,6,1,2],[11,12,7,8,9,10,11,12,7,8],[17,18,13,14,16,17,18,13,14],[23,24,19,20,21,22,23,24,19,20]] ] )
    assert np.equal_array(ref,res) == True

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
    ref = np.array( [ [[0,19,24,23,22],[,0,13,18,17,16],[0,1,2,3,4],[0,7,8,9,10],[0,13,14,15,16],[0,19,20,21,22],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True

# -- total grid
def test_6x4_6x4_V_T_total():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_UT, bnd=('close','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,19,24,23,22,21,20,0,0],[0,0,13,18,17,16,15,14,0,0],[0,0,1,2,3,4,5,6,0,0],[0,0,7,8,9,10,11,12,0,0],[0,0,13,14,15,16,17,18,0,0],[0,0,19,20,21,22,23,24,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True


# ====================================================================

# global grid - F grid, T fold point
folds_FT = set_fold_trf('F','T')

# -- cross top bnd
def test_6x4_2x1_F_T_top():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=2, fold_param=folds_FT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18,19,20,21,22,23,24]).reshape(12,1,order='F')).transpose()
    ref = np.array( [[[24,23,22,21,20,19],[18,17,16,15,14,13]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[24,23,22,21,20,19],[18,17,16,15,14,13],[1,2,3,4,5,6],[7,8,9,10,11,12],[13,14,15,16,17,18]] ] )
    assert np.equal_array(ref,res) == True

# -- upper left
def test_6x4_2x1_F_T_upleft():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=0, fold_param=folds_FT, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (2,2)
    assert hls.close == 2
    # segment
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18,19,20,21,22,23,24]).reshape(12,1,order='F')).transpose()
    ref = np.array( [[[20,19,24,23,22,21],[14,13,18,17,16,15]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,24,23,22,21],[0,0,18,17,16,15],[0,0,1,2,3,4],[0,0,7,8,9,10],[0,0,13,14,15,16]] ] )
    assert np.equal_array(ref,res) == True

# -- upper right
def test_6x4_2x1_F_T_upright():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=4, fold_param=folds_FT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-2,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild halos
    res = hls.rebuild_halos(np.array([13,14,15,16,17,18,19,20,21,22,23,24]).reshape(12,1,order='F')).transpose()
    ref = np.array( [[[22,21,20,19,24,23],[16,15,14,13,18,17]]] )
    assert np.equal_array(ref,res) == True
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[22,21,20,19,24,23],[16,15,14,13,18,17],[3,4,5,6,1,2],[9,10,11,12,7,8],[15,16,17,18,13,14]] ] )
    assert np.equal_array(ref,res) == True

# -- top line
def test_6x4_6x1_F_T_tline():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(2,1), offset=6, fold_param=folds_FT, bnd=('close','nfold') )
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == 2
    # segment
    res = hls.segment()
    assert res == ([0],[24])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,18,17,16,15,14,13,0,0],[0,0,1,2,3,4,5,6,0,0],[0,0,7,8,9,10,11,12,0,0],[0,0,13,14,15,16,17,18,0,0],[0,0,19,20,21,22,23,24,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- left column
def test_6x4_1x4_F_T_lcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=1, fold_param=folds_FT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (1,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,5,11],[4,5,13])
    # rebuild grid
    grid = np.array([1,2,3,4,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[19,24,23,22,21],[13,18,17,16,15],[6,1,2,3,4],[12,7,8,9,10],[18,13,14,15,16],[24,19,20,21,22],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- right column
def test_6x4_1x4_F_T_rcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=4, fold_param=folds_FT, bnd=('close','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-1,2)
    assert hls.close == -1
    # segment
    res = hls.segment()
    assert res == ([0,2,8],[1,5,16])
    # rebuild grid
    grid = np.array([1,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[22,21,20,19,0],[16,15,14,13,0],[3,4,5,6,0],[9,10,11,12,0],[15,16,17,18,0],[21,22,23,24,0],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- total grid
def test_6x4_6x4_F_T_total():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_UT, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[20,19,24,23,22,21,20,19,24,23],[14,13,18,17,16,15,14,13,18,17],[5,6,1,2,3,4,5,6,1,2],[11,12,7,8,9,10,11,12,7,8],[17,18,13,14,15,16,17,18,13,14],[23,24,19,20,21,22,23,24,19,20],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True


# ====================================================================

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
    assert np.equal_array(ref,res) == True

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
    ref = np.array( [ [[8,7,12,11,10],[2,1,6,5,4],[5,6,1,2,3,4],[5,6,1,2,3],[11,12,7,8,9],[17,18,13,14,15]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True
    
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
    assert np.equal_array(ref,res) == True

# -- left column
def test_6x4_1x4_T_F_lcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=3, fold_param=folds_TF, bnd=('close','nfold') )
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
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True


# ====================================================================

# global grid - V grid, F fold point
folds_VF = set_fold_trf('V','F')

# -- cross top bnd
def test_6x4_1x3_V_F_top():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(1,3), offset=3, fold_param=folds_VF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([2,7,14,20],[3,4,3,3])
    # rebuild grid
    grid = np.array([3,4,5,8,9,10,11,15,16,17,21,22,23])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[10,9,8],[3,4,5],[9,10,11],[15,16,17],[21,22,23]] ] )
    assert np.equal_array(ref,res) == True

# -- upper left
def test_6x4_1x1_V_F_upleft():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,1), offset=3, fold_param=folds_VF, bnd=('close','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (2,2)
    assert hls.close == 2
    # segment
    res = hls.segment()
    assert res == ([0,4],[3,14])
    # rebuild grid
    grid = np.array([1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18])
    res = hls.rebuild(grid.reshape(17,1,order='F')).transpose()
    ref = np.array( [ [[0,0,18,17,16],[0,0,12,11,10],[0,0,1,2,3],[0,0,7,8,9],[0,0,13,14,15]] ] )
    assert np.equal_array(ref,res) == True

# -- upper right
def test_6x4_1x1_V_F_upright():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,1), offset=5, fold_param=folds_VF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-2,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,3],[2,15])
    # rebuild grid
    grid = np.array([1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])
    res = hls.rebuild(grid.reshape(17,1,order='F')).transpose()
    ref = np.array( [ [[15,14,13,18,17],[9,8,7,12,11],[4,5,6,1,2],[10,11,12,7,8],[16,17,18,13,14]] ] )
    assert np.equal_array(ref,res) == True

# -- top line
def test_6x4_6x2_V_F_tline():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,2), offset=0, fold_param=folds_VF, bnd=('close','nfold') )
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == 1
    # segment
    res = hls.segment()
    assert res == ([0],[18])
    # rebuild grid
    res = hls.rebuild(np.arange(18).reshape(18,1,order='F')+1).transpose()
    ref = np.array( [ [[0,12,11,10,9,8,7,0],[0,1,2,3,4,5,6,0],[0,7,8,9,10,11,12,0],[0,13,14,15,16,17,18,0]] ] )
    assert np.equal_array(ref,res) == True

# -- left column
def test_6x4_1x4_V_F_lcol():
    hls = NFHalo( size=2, global_grid=(6,4), local_grid=(1,4), offset=0, fold_param=folds_VF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (2,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,4,22],[3,17,2])
    # rebuild grid
    grid = np.array([1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24])
    res = hls.rebuild(grid.reshape(22,1,order='F')).transpose()
    ref = np.array( [ [[14,13,18,17,16],[8,7,12,11,10],[5,6,1,2,3],[11,12,7,8,9],[17,18,13,14,15],[23,24,19,20,21],[0,0,0,0,0],[0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- right column
def test_6x4_1x4_V_F_rcol():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(1,4), offset=5, fold_param=folds_VF, bnd=('close','nfold') )
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-1,1)
    assert hls.close == -1
    # segment
    res = hls.segment()
    assert res == ([0,4,10,16,22],[1,4,3,3,2])
    # rebuild grid
    grid = np.array([1,5,6,7,8,11,12,13,17,18,19,23,24])
    res = hls.rebuild(grid.reshape(13,1,order='F')).transpose()
    ref = np.array( [ [[8,7,0],[5,6,0],[11,12,0],[17,18,0],[23,24,0],[0,0,0]] ] )
    assert np.equal_array(ref,res) == True

# -- total grid
def test_6x4_6x4_V_F_total():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_VF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,1)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[7,12,11,10,9,8,7,12],[6,1,2,3,4,5,6,1],[12,7,8,9,10,11,12,7],[18,13,14,15,16,17,18,13],[24,19,20,21,22,23,24,19],[0,0,0,0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True


# ====================================================================

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
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid =
    res = hls.rebuild(np.arange(12).reshape(12,1,order='F')+1).transpose()
    ref = np.array( [ [[11,10,9,8,7,12],[1,2,3,4,5,6],[7,8,9,10,11,12]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,3,7,8,9,10,11])
    res = hls.rebuild(grid.reshape(8,1,order='F')).transpose()
    ref = np.array( [ [[11,10,9],[1,2,3],[7,8,9]] ] )
    assert np.equal_array(ref,res) == True

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
    assert np.equal_array(ref,res) == True
    # rebuild grid
    grid = np.array([1,2,4,5,6,7,8,10,11,12,13,14,16,17,18,19,20,22,23,24])
    res = hls.rebuild(grid.reshape(20,1,order='F')).transpose()
    ref = np.array( [ [[8,7,12,11,10],[4,5,6,1,2],[10,11,12,7,8],[16,17,18,13,14],[22,23,24,19,20]] ] )
    assert np.equal_array(ref,res) == True

# -- total grid
def test_6x4_6x4_F_F_total():
    hls = NFHalo( size=1, global_grid=(6,4), local_grid=(6,4), offset=0, fold_param=folds_FF, bnd=('cyclic','nfold') )
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,2)
    assert hls.close == 0
    # segment
    res = hls.segment()
    assert res == ([0,6,12,18],[6,6,6,6])
    # rebuild grid
    res = hls.rebuild(np.arange(24).reshape(24,1,order='F')+1).transpose()
    ref = np.array( [ [[13,18,17,16,15,14,13,18,17,16],[7,12,11,10,9,8,7,12,11,10],[5,6,1,2,3,4,5,6,1,2],[11,12,7,8,9,10,11,12,7,8],[17,18,13,14,15,16,17,18,13,14],[23,24,19,20,21,22,23,24,19,20],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]] ] )
    assert np.equal_array(ref,res) == True

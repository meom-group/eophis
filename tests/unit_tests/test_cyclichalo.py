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


# ==================
# test cyclichalo.py
# ==================
from eophis.domain.cyclichalo import CyclicHalo

# global 9x9
# -- cross top bnd
def test_9x9_3x3_1_halo_top():
    hls = CyclicHalo(size=1, global_grid=(9,9), local_grid=(3,3), offset=3, bnd=('cyclic','close'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,1)
    assert hls.close == (0,1)
    seg = hls.segment()
    assert seg == ([75,74,78,2,6,11,15,20,24,30,29,33], [3,1,1,1,1,1,1,1,1,3,1,1])
    grid = np.array([3,4,5,6,7,12,13,14,15,16,21,22,23,24,25,30,31,32,33,34,75,76,77,78,79])
    res = hls.rebuild(grid.reshape(25,1,order='F')).transpose()
    ref = np.array( [ [[0,0,0,0,0],[3,4,5,6,7],[12,13,14,15,16],[21,22,23,24,25],[30,31,32,33,34]] ] )
    assert np.array_equal(res,ref) == True

# -- cross bottom bnd
def test_9x9_3x3_3_halo_bot():
    hls = CyclicHalo(size=3, global_grid=(9,9), local_grid=(3,3), offset=48, bnd=('close','cyclic'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (0,-2)
    assert hls.close == (0,0)
    seg = hls.segment()
    assert seg == ([21,18,24,30,27,33,39,36,42,45,51,54,60,63,69,75,72,78,3,0,6,12,9,15], [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3])
    res = hls.rebuild(np.arange(81).reshape(81,1,order='F')+1).transpose()
    ref = np.array( [ [[19,20,21,22,23,24,25,26,27], [28,29,30,31,32,33,34,35,36], [37,38,39,40,41,42,43,44,45], [46,47,48,49,50,51,52,53,54], [55,56,57,58,59,60,61,62,63], [64,65,66,67,68,69,70,71,72], [73,74,75,76,77,78,79,80,81], [1,2,3,4,5,6,7,8,9],[10,11,12,13,14,15,16,17,18]] ] )
    assert np.array_equal(res,ref) == True

# -- cross left bnd
def test_9x9_3x3_2_halo_left():
    hls = CyclicHalo(size=2, global_grid=(9,9), local_grid=(2,2), offset=28, bnd=('cyclic','close'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (1,0)
    assert hls.close == (0,0)
    seg = hls.segment()
    assert seg == ([10,17,9,12,19,26,18,21,35,27,30,44,36,39,46,53,45,48,55,62,54,57], [2,1,1,2,2,1,1,2,1,1,2,1,1,2,2,1,1,2,2,1,1,2])
    grid = np.array([10,11,12,13,14,18,19,20,21,22,23,27,28,29,30,31,32,36,37,38,39,40,41,45,46,47,48,49,50,54,55,56,57,58,59,63])
    res = hls.rebuild(grid.reshape(36,1,order='F')).transpose()
    ref = np.array( [ [[18,10,11,12,13,14],[27,19,20,21,22,23],[36,28,29,30,31,32],[45,37,38,39,40,41],[54,46,47,48,49,50],[63,55,56,57,58,59]] ] )
    assert np.array_equal(res,ref) == True

# -- cross right bnd
def test_9x9_3x3_1_halo_right():
    hls = CyclicHalo(size=1, global_grid=(9,9), local_grid=(3,3), offset=42, bnd=('close','close'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-1,0)
    assert hls.close == (-1,0)
    seg = hls.segment()
    assert seg == ([33,32,27,41,36,50,45,59,54,69,68,63], [3,1,1,1,1,1,1,1,1,3,1,1])
    grid = np.array([ 28,33,34,35,36,37,42,43,44,45,46,51,52,53,54,55,60,61,62,63,64,69,70,71,72 ])
    res = hls.rebuild(grid.reshape(25,1,order='F')).transpose()
    ref = np.array( [ [[33,34,35,36,0],[42,43,44,45,0],[51,52,53,54,0],[60,61,62,63,0],[69,70,71,72,0]] ] )
    assert np.array_equal(res,ref) == True

# ====================

# global 5x3
# -- left column
def test_5x3_2x3_1_halo_lcol():
    hls = CyclicHalo(size=1, global_grid=(5,3), local_grid=(2,3), offset=0, bnd=('close','cyclic'))
    assert hls.full_dim == (False,True)
    assert hls.shifts == (1,0)
    assert hls.close == (1,0)
    seg = hls.segment()
    assert seg == ([4,2,9,7,14,12], [1,1,1,1,1,1])
    grid = np.array([1,2,3,5,6,7,8,10,11,12,13,15])
    res = hls.rebuild(grid.reshape(12,1,order='F')).transpose()
    ref = np.array( [ [[0,11,12,13],[0,1,2,3],[0,6,7,8],[0,11,12,13],[0,1,2,3]] ] )
    assert np.array_equal(res,ref) == True

# -- intern column
def test_5x3_2x3_1_halo_icol():
    hls = CyclicHalo(size=1, global_grid=(5,3), local_grid=(2,3), offset=2, bnd=('cyclic','cyclic'))
    assert hls.full_dim == (False,True)
    assert hls.shifts == (0,0)
    assert hls.close == (0,0)
    seg = hls.segment()
    assert seg == ([1,4,6,9,11,14], [1,1,1,1,1,1])
    grid = np.array([2,3,4,5,7,8,9,10,12,13,14,15])
    res = hls.rebuild(grid.reshape(12,1,order='F')).transpose()
    ref = np.array( [ [[12,13,14,15],[2,3,4,5],[7,8,9,10],[12,13,14,15],[2,3,4,5]] ] )
    assert np.array_equal(res,ref) == True

# -- right column
def test_5x3_2x3_1_halo_rcol():
    hls = CyclicHalo(size=1, global_grid=(5,3), local_grid=(1,3), offset=4, bnd=('cyclic','close'))
    assert hls.full_dim == (False,True)
    assert hls.shifts == (-1,0)
    assert hls.close == (0,1)
    seg = hls.segment()
    assert seg == ([3,0,8,5,13,10], [1,1,1,1,1,1])
    grid = np.array([1,4,5,6,9,10,11,14,15])
    res = hls.rebuild(grid.reshape(9,1,order='F')).transpose()
    ref = np.array( [ [[0,0,0],[4,5,1],[9,10,6],[14,15,11],[0,0,0]] ] )
    assert np.array_equal(res,ref) == True

# ====================

# global 3x5
# -- top line
def test_3x5_3x2_1_halo_tline():
    hls = CyclicHalo(size=1, global_grid=(3,5), local_grid=(3,2), offset=0, bnd=('close','cyclic'))
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,1)
    assert hls.close == (1,0)
    seg = hls.segment()
    assert seg == ([12,6],[3,3])
    grid = np.array([1,2,3,4,5,6,7,8,9,13,14,15])
    res = hls.rebuild(grid.reshape(12,1,order='F')).transpose()
    ref = np.array( [ [[0,13,14,15,0],[0,1,2,3,0],[0,4,5,6,0],[0,7,8,9,0]] ] )
    assert np.array_equal(res,ref) == True

# -- intern line
def test_3x5_3x1_1_halo_iline():
    hls = CyclicHalo(size=1, global_grid=(3,5), local_grid=(3,1), offset=6, bnd=('close','close'))
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,0)
    assert hls.close == (1,0)
    seg = hls.segment()
    assert seg == ([3,9],[3,3])
    grid = np.array([4,5,6,7,8,9,10,11,12])
    res = hls.rebuild(grid.reshape(9,1,order='F')).transpose()
    ref = np.array( [ [[0,4,5,6,0],[0,7,8,9,0],[0,10,11,12,0]] ] )
    assert np.array_equal(res,ref) == True

# -- bottom line
def test_3x5_3x1_1_halo_bline():
    hls = CyclicHalo(size=1, global_grid=(3,5), local_grid=(3,1), offset=12, bnd=('cyclic','close'))
    assert hls.full_dim == (True,False)
    assert hls.shifts == (0,-1)
    assert hls.close == (0,-1)
    seg = hls.segment()
    assert seg == ([9,0],[3,3])
    grid = np.array([1,2,3,10,11,12,13,14,15])
    res = hls.rebuild(grid.reshape(9,1,order='F')).transpose()
    ref = np.array( [ [[12,10,11,12,10],[15,13,14,15,13],[0,0,0,0,0]] ] )
    assert np.array_equal(res,ref) == True

# ====================

# global 6x6
# -- upper left
def test_6x6_2x2_2_halo_upleft():
    hls = CyclicHalo(size=2, global_grid=(6,6), local_grid=(2,2), offset=0, bnd=('close','cyclic'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (2,2)
    assert hls.close == (2,0)
    seg = hls.segment()
    assert seg == ([24,28,26,30,34,32,4,2,10,8,12,16,14,18,22,20], [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2])
    res = hls.rebuild(np.arange(36).reshape(36,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,25,26,27,28],[0,0,31,32,33,34],[0,0,1,2,3,4],[0,0,7,8,9,10],[0,0,13,14,15,16],[0,0,19,20,21,22]] ] )
    assert np.array_equal(res,ref) == True

# global 4x4
# -- upper right
def test_4x4_2x2_1_halo_upright():
    hls = CyclicHalo(size=1, global_grid=(4,4), local_grid=(2,2), offset=2, bnd=('cyclic','close'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-1,1)
    assert hls.close == (0,1)
    seg = hls.segment()
    assert seg == ([14,13,12,1,0,5,4,10,9,8], [2,1,1,1,1,1,1,2,1,1])
    res = hls.rebuild(np.arange(16).reshape(16,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,0,0],[2,3,4,1],[6,7,8,5],[10,11,12,9]] ] )
    assert np.array_equal(res,ref) == True

# -- lower left
def test_4x4_2x2_1_halo_loleft():
    hls = CyclicHalo(size=1, global_grid=(4,4), local_grid=(2,2), offset=8, bnd=('cyclic','cyclic'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (1,-1)
    assert hls.close == (0,0)
    seg = hls.segment()
    assert seg == ([4,7,6,11,10,15,14,0,3,2], [2,1,1,1,1,1,1,2,1,1])
    res = hls.rebuild(np.arange(16).reshape(16,1,order='F')+1).transpose()
    ref = np.array( [ [[8,5,6,7],[12,9,10,11],[16,13,14,15],[4,1,2,3]] ] )
    assert np.array_equal(res,ref) == True

# -- lower right
def test_4x4_2x2_1_halo_loright():
    hls = CyclicHalo(size=1, global_grid=(4,4), local_grid=(2,2), offset=10, bnd=('close','close'))
    assert hls.full_dim == (False,False)
    assert hls.shifts == (-1,-1)
    assert hls.close == (-1,-1)
    seg = hls.segment()
    assert seg == ([6,5,4,9,8,13,12,2,1,0], [2,1,1,1,1,1,1,2,1,1])
    res = hls.rebuild(np.arange(16).reshape(16,1,order='F')+1).transpose()
    ref = np.array( [ [[6,7,8,0],[10,11,12,0],[14,15,16,0],[0,0,0,0]] ] )
    assert np.array_equal(res,ref) == True

# global grid 4x4
# -- total grid
def test_4x4_4x4_1_halo_total():
    hls = CyclicHalo(size=1, global_grid=(4,4), local_grid=(4,4), offset=0, bnd=('cyclic','close'))
    assert hls.full_dim == (True,True)
    assert hls.shifts == (0,0)
    assert hls.close == (0,1)
    seg = hls.segment()
    assert seg == ([],[])
    res = hls.rebuild(np.arange(16).reshape(16,1,order='F')+1).transpose()
    ref = np.array( [ [[0,0,0,0,0,0],[4,1,2,3,4,1],[8,5,6,7,8,5],[12,9,10,11,12,9],[16,13,14,15,16,13],[0,0,0,0,0,0]] ] )
    assert np.array_equal(res,ref) == True

# ====================
# 3D grids

# global grid 5x5x2
# -- upper right
def test_5x5x2_2x2x2_1_halo_upright():
    hls = CyclicHalo(size=1, global_grid=(5,5), local_grid=(2,2), offset=3, bnd=('cyclic','close'))
    grid = np.array([1,3,4,5,6,8,9,10,11,13,14,15,21,23,24,25,26,28,29,30,31,33,34,35,36,38,39,40,46,48,49,50])
    res = hls.rebuild(grid.reshape(16,2,order='F')).transpose()
    ref = np.array( [[[0,0,0,0],[3,4,5,1],[8,9,10,6],[13,14,15,11]],[[0,0,0,0],[28,29,30,26],[33,34,35,31],[38,39,40,36]]] )
    assert np.array_equal(res,ref) == True

# global grid 4x4x2
# -- total grid
def test_4x4x2_4x4x2_1_halo_total():
    hls = CyclicHalo(size=1, global_grid=(4,4), local_grid=(4,4), offset=0, bnd=('close','cyclic'))
    res = hls.rebuild(np.arange(32).reshape(16,2,order='F')+1).transpose()
    ref = np.array( [ [[0,13,14,15,16,0],[0,1,2,3,4,0],[0,5,6,7,8,0],[0,9,10,11,12,0],[0,13,14,15,16,0],[0,1,2,3,4,0]] , [[0,29,30,31,32,0],[0,17,18,19,20,0],[0,21,22,23,24,0],[0,25,26,27,28,0],[0,29,30,31,32,0],[0,17,18,19,20,0]] ] )
    assert np.array_equal(res,ref) == True

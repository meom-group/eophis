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


# ============
# test halo.py
# ============
from eophis.coupling.halo import HaloGrid

# global grid 9x9
# -- local grid 3x3
def test_9x9_3x3_no_halo():
    hls = HaloGrid(size=0 , global_grid=(9,9), local_grid=(3,3), offset=12)
    seg = hls.segment()
    assert seg == ([],[])
    res = np.array([1,2,3,10,11,12,19,20,21]).reshape(9,1,order='F')[:,:,0]
    res = hls.rebuild( res )
    ref = np.array( [[7,9],[6,7],[20,21],[12,14],[18,19],[1,5]] )
    assert np.array_equal(res,ref) == True

def test_9x9_3x3_1_halo():
    hls = HaloGrid(size=1 , global_grid=(9,9), local_grid=(3,3), offset=31)
    seg = hls.segment()
    assert seg == ([21,30,34,39,43,48,52,57],[5,1,1,1,1,1,1,5])

def test_9x9_3x3_1_halo_offset():
    hls = HaloGrid(size=1 , global_grid=(9,9), local_grid=(3,3), offset=50)
    seg = hls.segment()
    assert seg == ([40,49,53,58,62,67,71,76],[5,1,1,1,1,1,1,5])
    
def test_9x9_3x3_2_halo():
    hls = HaloGrid(size=2 , global_grid=(9,9), local_grid=(3,3), offset=20)
    seg = hls.segment()
    assert seg == ([0,9,18,23,27,32,36,41,45,54], [7,7,2,2,2,2,2,2,7,7])
    
def test_9x9_3x3_2_halo_offset
    hls = HaloGrid(size=2 , global_grid=(9,9), local_grid=(3,3), offset=39)
    seg = hls.segment()
    assert seg == ([19,28,37,42,46,51,55,60,64,73], [7,7,2,2,2,2,2,2,7,7])
    
# -- local grid 4x5
def test_9x9_4x5_2_halo_local_grid
    hls = HaloGrid(size=2 , global_grid=(9,9), local_grid=(4,5), offset=20)
    seg = hls.segment()
    assert seg == ([0,9,18,24,27,33,36,42,45,51,54,60,63,72], [8,8,2,2,2,2,2,2,2,2,2,2,8,8])
    
# -- segment side halos
def test_segment_side_halos():
    hls = HaloGrid(size=2 , global_grid=(9,9), local_grid=(4,5), offset=20)
    res = hls.segment_side_halos(21,19)
    assert res == ([19],[2])
    res = hls.segment_side_halos(19,17)
    assert res == ([26,18],[1,1])
    res = hls.segment_side_halos(18,16)
    assert res == ([25],[2])
    res = hls.segment_side_halos(33,35)
    assert res == ([35,27],[1,1])
    res = hls.segment_side_halos(34,16)
    assert res == ([27],[2])
    
# global grid 6x4
# -- local grid 2x2
def test_6x4_2x2_1_halos():
    hls = HaloGrid(size=1 , global_grid=(6,4), local_grid=(2,2), offset=8)
    seg = hls.segment()
    assert seg == ([1,7,10,13,16,19],[4,1,1,1,1,4])
    
# -- local grid 1x1
def test_6x4_1x1_1_halos():
    hls = HaloGrid(size=1 , global_grid=(6,4), local_grid=(1,1), offset=16)
    seg = hls.segment()
    assert seg == ([9,15,17,21],[3,1,1,3])

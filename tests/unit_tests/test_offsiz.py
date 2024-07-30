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
# test offsiz.py
# ==============
from eophis.domain.offsiz import set_fold_trf, list_to_slices, grid_to_offsets_sizes, clean_for_oasis

def test_set_fold_trf():
    assert set_fold_trf('T','T') == [1,1,0]
    assert set_fold_trf('U','T') == [1,0,0]
    assert set_fold_trf('V','T') == [2,1,0]
    assert set_fold_trf('F','T') == [2,0,0]
    assert set_fold_trf('T','F') == [0,0,0]
    assert set_fold_trf('U','F') == [0,-1,0]
    assert set_fold_trf('V','F') == [1,0,0]
    assert set_fold_trf('F','F') == [1,-1,0]

def test_list_to_slices():
    ref = np.array( [[7,9],[6,7],[20,21],[12,14],[18,19],[1,5]] )
    res = list_to_slices( [7,8,6,20,12,13,18,1,2,3,4] )
    assert np.array_equal(res,ref) == True

def test_grid_to_offsets_sizes():
    grid = np.array( [7,8,9,12,13,18,22,1,2,3,4] )
    offsets, sizes = grid_to_offsets_sizes(grid)
    assert offsets == [6,11,17,21,0]
    assert sizes == [3,2,1,1,4]

def test_clean_for_oasis_overlap():
    off = [0,3,11,17,21,0,5]
    siz = [3,3,2,3,1,4,3]
    offsets, sizes = clean_for_oasis(off,siz)
    assert offsets == [0,11,17,21]
    assert sizes == [8,2,3,1]

def test_clean_for_oasis_clean():
    off = [0,11,17,21]
    siz = [8,2,3,1]
    offsets, sizes = clean_for_oasis(off,siz)
    assert offsets ==  [0,11,17,21]
    assert sizes == [8,2,3,1]

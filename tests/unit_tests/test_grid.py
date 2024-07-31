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

# ============
# test grid.py
# ============
from eophis.domain.grid import Grid, select_halo_type
from eophis.domain.halo import HaloGrid
from eophis.domain.cyclichalo import CyclicHalo
from eophis.domain.nfhalo import NFHalo

# test halo selector
def test_halo_selector():
    # no halos - core and no core
    hls = select_halo_type(grd='T', fold='T', bnd=('close','close'), halo_size=0, global_grid=(9,9), local_grid=(3,3), offset=0 )
    assert isinstance(hls,HaloGrid)
    hls = select_halo_type(grd='T', fold='T', bnd=('close','cyclic'), halo_size=0, global_grid=(9,9), local_grid=(3,3), offset=31 )
    assert isinstance(hls,HaloGrid)
    # halos in core grid
    hls = select_halo_type(grd='T', fold='T', bnd=('close','cyclic'), halo_size=1, global_grid=(9,9), local_grid=(3,3), offset=31 )
    assert isinstance(hls,HaloGrid)
    # halos in bnd
    hls = select_halo_type(grd='T', fold='T', bnd=('cyclic','close'), halo_size=1, global_grid=(9,9), local_grid=(3,3), offset=27 )
    assert isinstance(hls,CyclicHalo)
    # halos in bnd + intern line
    hls = select_halo_type(grd='T', fold='T', bnd=('close','close'), halo_size=2, global_grid=(9,9), local_grid=(3,3), offset=41 )
    assert isinstance(hls,CyclicHalo)
    # fold halos in core grid
    hls = select_halo_type(grd='T', fold='T', bnd=('close','nfold'), halo_size=1, global_grid=(6,4), local_grid=(2,2), offset=8 )
    assert isinstance(hls,HaloGrid)
    # fold halos in top bnd
    hls = select_halo_type(grd='T', fold='T', bnd=('close','nfold'), halo_size=2, global_grid=(6,4), local_grid=(1,1), offset=3 )
    assert isinstance(hls,NFHalo)
    # fold halos in bottom bnd
    hls = select_halo_type(grd='T', fold='T', bnd=('cyclic','nfold'), halo_size=1, global_grid=(6,4), local_grid=(1,1), offset=18 )
    assert isinstance(hls,CyclicHalo)

# ===========================
# grid with core and cyclic / close halos

def test_bnd_attributes_cyclic_close():
    grd = Grid('DEMO_GRID', nx=9, ny=9, halo_size=0, bnd=('clOse','cYclic'), grd='T', fold='T')
    assert grd.label == 'DEMO_GRID'
    assert grd.size == (9,9)
    assert grd.halo_size == 0
    assert grd.bnd == ('close','cyclic')
    assert grd.fold == 'T'
    assert grd.fold == 'T'
    
def test_decompose_cyclic_close():
    grd = Grid('DEMO_GRID', nx=9, ny=9, halo_size=0, bnd=('clOse','cYclic'), grd='T', fold='T')
    assert grd.decompose(1) == ((9,),(9,))
    assert grd.decompose(2) == ((5,4),(9,))
    assert grd.decompose(7) == ((2,2,1,1,1,1,1),(9,))
    assert grd.decompose(9) == ((3,3,3),(3,3,3))

def test_subdomain_cyclic_close_first():
    grd = Grid('DEMO_GRID', nx=9, ny=9, halo_size=0, bnd=('clOse','cYclic'), grd='T', fold='T')
    grd.make_local_subdomain(0,1)
    assert grd.as_box_partition() == (0,9,9,9)
    assert grd.as_orange_partition() == ([0],[81],81)
    # generate and rebuild
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array()) )
    assert rcv_fld.shape == (9,9,1)

def test_subdomain_cyclic_close_second():
    grd = Grid('DEMO_GRID', nx=9, ny=9, halo_size=0, bnd=('clOse','cYclic'), grd='T', fold='T')
    grd.make_local_subdomain(3,9)
    assert grd.as_box_partition() == (27,3,3,9)
    assert grd.as_orange_partition() == ([27,36,45],[3,3,3],81)
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array()) )
    assert rcv_fld.shape == (3,3,1)

def test_subdomain_cyclic_close_third():
    grd = Grid('DEMO_GRID', nx=9, ny=9, halo_size=2, bnd=('clOse','cYclic'), grd='T', fold='T')
    grd.make_local_subdomain(5,9)
    assert grd.as_box_partition() == (33,3,3,9)
    assert grd.as_orange_partition() == ([9,13,22,31,40,49,58,67],[2,7,7,7,7,7,7,5],81)
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array(3)) )
    assert rcv_fld.shape == (3,3,3)

def test_subdomain_cyclic_close_fourth():
    grd = Grid('DEMO_GRID', nx=9, ny=9, halo_size=1, bnd=('clOse','cYclic'), grd='T', fold='T')
    grd.make_local_subdomain(1,2)
    assert grd.as_box_partition() == (5,4,9,9)
    assert grd.as_orange_partition() == ([0,4,13,22,31,40,49,58,67,76],[1,6,6,6,6,6,6,6,6,5],81)
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array()) )
    assert rcv_fld.shape == (4,9,1)


# ===========================
# grid with north fold halos

def test_bnd_attributes_NF():
    grd = Grid('eORCA1', nx=6, ny=4, halo_size=0, bnd=('dirichlet','nfold'), grd='V', fold='T')
    assert grd.label == 'eORCA1'
    assert grd.size == (6,4)
    assert grd.halo_size == 0
    assert grd.bnd == ('close','nfold')
    assert grd.grd == 'V'
    assert grd.fold == 'T'
    
def test_decompose_NF():
    grd = Grid('eORCA1', nx=6, ny=4, halo_size=0, bnd=('dirichlet','nfold'), grd='V', fold='T')
    assert grd.decompose(3) == ((2,2,2),(4,))
    assert grd.decompose(4) == ((3,3),(2,2))

def test_subdomain_NF_first():
    grd = Grid('eORCA1', nx=6, ny=4, halo_size=0, bnd=('dirichlet','nfold'), grd='V', fold='T')
    grd.make_local_subdomain(1,2)
    assert grd.as_box_partition() == (3,3,4,6)
    assert grd.as_orange_partition() == ([3,9,15,21],[3,3,3,3],24)
    # generate and rebuild
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array(2)) )
    assert rcv_fld.shape == (3,4,2)

def test_subdomain_NF_second():
    grd = Grid('eORCA1', nx=6, ny=4, halo_size=1, bnd=('dirichlet','nfold'), grd='V', fold='T')
    grd.make_local_subdomain(2,3)
    assert grd.as_box_partition() == (4,2,4,6)
    assert grd.as_orange_partition() == ([0,3,9,21],[1,4,10,3],24)
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array()) )
    assert rcv_fld.shape == (2,4,1)

def test_subdomain_NF_third():
    grd = Grid('eORCA1', nx=6, ny=4, halo_size=1, bnd=('dirichlet','nfold'), grd='V', fold='T')
    grd.make_local_subdomain(0,4)
    assert grd.as_box_partition() == (0,3,2,6)
    assert grd.as_orange_partition() == ([0,5,11],[4,5,7],24)
    rcv_fld = grd.format_sending_array( grd.rebuild(grd.generate_receiving_array(2)) )
    assert rcv_fld.shape == (3,2,2)

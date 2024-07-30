import os
import shutil
import logging
import inspect
from unittest.mock import MagicMock, patch
from mpi4py import MPI
import pytest
#
import eophis

# ========
# cleaning
# ========
#@pytest.fixture(scope="session",autouse=True)
#def clean_files():
    #yield
    #for file_name in ["eophis.out", "eophis.err"]:
        #if os.path.exists(file_name):
            #os.remove(file_name)
    #if os.path.exists("test_namcouple"):
    #    os.remove("test_namcouple")
    #shutil.rmtree("__pycache__")


# ==============
# test tunnel.py
# ==============
from eophis.coupling.namcouple import Namcouple, register_tunnels
from eophis.coupling.tunnel import Tunnel
from eophis.utils.params import set_mode

def test_register_tunnels():
    configs = [
        {
            "label": "test_tunnel",
            "grids": {"grid1": { 'npts' : (10,10) , 'halos' : 5, 'bnd' : ('close','close') } },
            "exchs": [{"grd": "grid1", "in": ["var1"], "out": ["var2"], "freq": 3600, "lvl": 1}, \
                      {"grd": "grid1", "in": ["var0"], "out":[], "freq": -1, "lvl":3 }],
            "geo_aliases": {"var1": "VAR1_GEO", "var2": "VAR2_GEO"},
            "py_aliases": {"var1": "VAR1_PY", "var2": "VAR2_PY"}
        }
    ]

    set_mode('preprod')
    namcouple = Namcouple()
    tunnels = register_tunnels(configs)

    # tunnel creation
    assert len(tunnels) == 1
    assert tunnels[0].label == "test_tunnel"
    assert tunnels[0].grids['grid1'].label == "grid1"
    assert tunnels[0].grids['grid1'].size == (10,10)
    assert tunnels[0].grids['grid1'].bnd == ('close','close')
    assert tunnels[0].grids['grid1'].halo_size == 5
    assert tunnels[0].grids['grid1'].grd == 'T'
    assert tunnels[0].grids['grid1'].fold == 'T'
    assert tunnels[0].exchs == [{"grd": "grid1", "in": ["var1"], "out": ["var2"], "freq": 3600, "lvl": 1},{"grd": "grid1", "in": ["var0"], "out":[], "freq": -1, "lvl":3 }]
    assert tunnels[0].geo_aliases == {"var0" : "E_OUT_1", "var1": "VAR1_GEO", "var2": "VAR2_GEO"}
    assert tunnels[0].py_aliases ==  {"var0" : "M_IN_1" , "var1": "VAR1_PY", "var2": "VAR2_PY"}
    assert tunnels == namcouple.tunnels
    
    # tunnel method
    assert tunnels[0].arriving_list() == ['var1']
    assert tunnels[0].departure_list() == ['var2']
    
    # namcouple content updated by tunnel registration
    section0 = 'VAR1_GEO VAR1_PY 1 3600 0 rst.nc EXPORTED\n10 10 10 10 grid1 grid1 LAG=0\nR 0 R 0'
    section1 = 'VAR2_PY VAR2_GEO 1 3600 0 rst.nc EXPORTED\n10 10 10 10 grid1 grid1 LAG=0\nR 0 R 0'
    eophis.info(namcouple._lines)
    assert section0 in namcouple._lines
    assert section1 in namcouple._lines

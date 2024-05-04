import os
import shutil
import logging
import inspect
from unittest.mock import MagicMock, patch
from mpi4py import MPI
import pytest
#
import eophis

@pytest.fixture(scope="session",autouse=True)
def clean_files():
    yield
    for file_name in ["eophis.out", "eophis.err"]:
        if os.path.exists(file_name):
            os.remove(file_name)
    if os.path.exists("test_namcouple"):
        os.remove("test_namcouple")
    shutil.rmtree("__pycache__")

def inquire_log_files():
    assert os.path.exists("eophis.out"), "log file 'eophis.out' does not exist"
    assert os.path.exists("eophis.err"), "log file 'eophis.err' does not exist"


# ==============
# test worker.py
# ==============
from eophis.utils.worker import Paral, set_local_communicator, make_subdomain

def test_set_local_communicator():
    new_comm = MagicMock(spec=MPI.Intracomm)
    new_rank = new_comm.Get_rank()
    set_local_communicator(new_comm)
    assert Paral.EOPHIS_COMM == new_comm
    assert Paral.RANK == new_rank

def test_make_subdomain():
    nx, ny, nsub = 4, 4, 6
    rankx, ranky = make_subdomain(nx, ny, nsub)
    assert rankx == (2,1,1)
    assert ranky == (2,2)

def test_make_subdomain_prime():
    nx, ny, nsub = 8, 5, 7
    rankx, ranky = make_subdomain(nx, ny, nsub)
    assert rankx == (2,1,1,1,1,1,1)
    assert ranky == (5,)

# ==============
# test params.py
# ==============
from eophis.utils.params import set_mode, Mode

def test_set_mode():
    set_mode('preprod')
    assert Mode.PREPROD == True
    assert Mode.PROD == False
    set_mode('prod')
    assert Mode.PREPROD == False
    assert Mode.PROD == True
    set_mode('invalid')
    assert Mode.PREPROD == False
    assert Mode.PROD == False


# ============
# test logs.py
# ============
from eophis.utils.logs import info, warning, abort, _Logbuffer, _logger_info, _logger_err

def test_info():
    _Logbuffer.store = False
    Paral.RANK = Paral.MASTER
    mock_logger_info = MagicMock(spec=logging.Logger)
    with patch('eophis.utils.logs._logger_info', mock_logger_info):
        info("Test message")
        mock_logger_info.info.assert_called_once_with("Test message")

def test_warning():
    caller = os.getcwd() + '/test_eophis.py'
    Paral.RANK = Paral.MASTER
    _Logbuffer.store = False
    mock_logger_err = MagicMock(spec=logging.Logger)
    mock_info = MagicMock()
    with patch('eophis.utils.logs._logger_err', mock_logger_err), \
         patch('eophis.utils.logs.info', mock_info):
        warning("Test warning")
        mock_logger_err.warning.assert_called_once_with("[RANK:0] from "+caller+" at line 88: Test warning")
        mock_info.assert_called_once_with('Warning raised by rank 0 ! See error log for details\n', 0)

def test_abort():
    caller = os.getcwd() + '/test_eophis.py'
    _Logbuffer.store = False
    mock_logger_err = MagicMock(spec=logging.Logger)
    mock_info = MagicMock()
    mock_quit_eophis = MagicMock()
    with patch('eophis.utils.logs._logger_err', mock_logger_err), \
         patch('eophis.utils.logs.info', mock_info), \
         patch('eophis.utils.logs.quit_eophis', mock_quit_eophis):
        abort("Test error")
        mock_logger_err.error.assert_called_once_with("[RANK:0] from "+caller+" at line 101: Test error")
        mock_info.assert_called_once_with('RUN ABORTED by rank 0 see error log for details', 0)
        mock_quit_eophis.assert_called_once()


# ===========
# namelist.py
# ===========
from eophis.coupling.namelist import FortranNamelist, raw_content, find, replace_line, find_and_replace_line, find_and_replace_char, write

@pytest.fixture
def namelist_file(tmpdir):
    file_content = """
&namelist1
    var1 = value1
    var2 = value2
/

&namelist2
    var3 = value3
    var4 = value4
/
"""
    file_path = os.path.join(tmpdir, "test_namelist.nml")
    with open(file_path, "w") as file:
        file.write(file_content)
    return file_path

def test_FortranNamelist(namelist_file):
    namelist = FortranNamelist(namelist_file)
    del namelist.raw[0]
    assert namelist.formatted['namelist1']['var1'] == 'value1'
    assert namelist.formatted['namelist2']['var4'] == 'value4'
    assert namelist.raw == ["&namelist1", "    var1 = value1", "    var2 = value2", "/", "", "&namelist2", "    var3 = value3", "    var4 = value4", "/"]

def test_raw_content(namelist_file):
    lines = raw_content(namelist_file)
    del lines[0]
    assert lines == ["&namelist1", "    var1 = value1", "    var2 = value2", "/", "", "&namelist2", "    var3 = value3", "    var4 = value4", "/"]

def test_find(namelist_file):
    lines = raw_content(namelist_file)
    del lines[0]
    pos = find(lines, "&namelist2")
    assert pos == 5

def test_replace_line(namelist_file):
    lines = raw_content(namelist_file)
    del lines[0]
    replace_line(lines, "&namelist2a", 6)
    assert lines[6] == "&namelist2a"

def test_find_and_replace_line(namelist_file):
    lines = raw_content(namelist_file)
    del lines[0]
    find_and_replace_line(lines, "&namelist1", "&namelist1a")
    assert lines[0] == "&namelist1a"
    assert lines[1] == "    var1 = value1"

def test_find_and_replace_char(namelist_file):
    lines = raw_content(namelist_file)
    del lines[0]
    find_and_replace_char(lines, "=", ":")
    assert lines[1] == "    var1 : value1"

def test_write(namelist_file, tmpdir):
    lines = ["&namelist1", "    var1 = value1", "    var2 = value2", "/", "", "&namelist2", "    var3 = value3", "    var4 = value4", "/"]
    output_file = os.path.join(tmpdir, "output_namelist.nml")
    write(lines, output_file, add_header=True)
    assert os.path.exists(output_file)
    with open(output_file, "r") as file:
        content = file.read()
        assert "MODIFIED BY EOPHIS" in content


# ============
# namcouple.py
# tunnel.py
# ============
from eophis.coupling.namcouple import Namcouple, register_tunnels, init_namcouple, write_coupling_namelist
from eophis.coupling.tunnel import Tunnel

def test_Namcouple():
    # Namcouple attributes protected by singleton
    infile = "test_namcouple"
    outfile = "test_namcouple"
    namcouple = Namcouple(infile, outfile)
    assert namcouple.infile != infile
    assert namcouple.outfile != outfile
    # reset does not override singleton protections
    namcouple._reset()
    assert namcouple.infile != infile
    assert namcouple.outfile != outfile
    # init_namcouple does
    init_namcouple(infile,outfile)
    namcouple = Namcouple(infile, outfile)
    assert namcouple.infile == infile
    assert namcouple.outfile == outfile
    assert namcouple.tunnels == []
    assert namcouple.comp == None
    assert namcouple._Nin == 0
    assert namcouple._Nout == 0
    assert namcouple._activated == False
    assert namcouple._lines == [ '$NFIELDS', '0', '$END', '############', '$RUNTIME', '0', '$END', '############', '$NLOGPRT', '1 0', '$END', '############', '$STRINGS', '#', '$END' ]
    
def test_register_tunnels():
    configs = [
        {
            "label": "test_tunnel",
            "grids": {"grid1": (10, 10, 0, 0)},
            "exchs": [{"grd": "grid1", "in": ["var1"], "out": ["var2"], "freq": 3600, "lvl": 1}, \
                      {"grd": "grid1", "in": ["var0"], "out":[], "freq": -1, "lvl":3 }],
            "geo_aliases": {"var1": "VAR1_GEO", "var2": "VAR2_GEO"},
            "py_aliases": {"var1": "VAR1_PY", "var2": "VAR2_PY"}
        }
    ]

    namcouple = Namcouple()
    tunnels = register_tunnels(configs)

    # tunnel creation
    assert len(tunnels) == 1
    assert tunnels[0].label == "test_tunnel"
    assert tunnels[0].grids == {"grid1": (10, 10, 0, 0)}
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
    assert section0 in namcouple._lines
    assert section1 in namcouple._lines
    # write OASIS namelist
    Paral.RANK = Paral.MASTER
    set_mode('preprod')
    write_coupling_namelist()
    assert os.path.exists("test_namcouple"), "file 'test_namcouple' has not been written"

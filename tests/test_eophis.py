import os
import numpy as np
from unittest.mock import MagicMock, patch
from mpi4py import MPI
#
import eophis
from eophis import Freqs, Grids
#
import pytest

# clean directory
@pytest.fixture(scope="session",autouse=True)
def clean_files():
    yield
    for file_name in ["eophis.out", "eophis.err"]:
        if os.path.exists(file_name):
            os.remove(file_name)

# Test presence of log files
def inquire_log_files():
    assert os.path.exists("eophis.out"), "log file 'eophis.out' does not exist"
    assert os.path.exists("eophis.err"), "log file 'eophis.err' does not exist"


# ==============
# test worker.py
# ==============
from eophis.utils.worker import Paral, set_local_communicator, make_subdomain, quit_eophis

def test_set_local_communicator():
    new_comm = MagicMock(spec=MPI.Intracomm)
    new_rank = 123
    set_local_communicator(new_comm)
    assert Paral.EOPHIS_COMM == new_comm
    assert Paral.RANK == new_rank

def test_make_subdomain():
    nx, ny, nsub = 4, 4, 6
    rankx, ranky = make_subdomain(nx, ny, nsub)
    assert rankx == (2,1,1)
    assert ranky == (2,2)

@patch.object(Paral.GLOBAL_COMM, 'Abort')
def test_quit_eophis(mock_abort):
    quit_eophis()
    mock_abort.assert_called_once_with(0)


# ==============
# test params.py
# ==============
from eophis.utils.params import set_mode

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
    mock_logger_info = MagicMock(spec=logging.Logger)
    with patch('mon_module_de_logs._logger_info', mock_logger_info):
        info("Test message")
        assert _Logbuffer.content == ["Test message"]
        mock_logger_info.info.assert_called_once_with("Test message")

def test_warning():
    mock_logger_err = MagicMock(spec=logging.Logger)
    mock_info = MagicMock()
    with patch('mon_module_de_logs._logger_err', mock_logger_err), \
         patch('mon_module_de_logs.info', mock_info):
        warning("Test warning")
        assert _Logbuffer.content == ["Test warning"]
        mock_logger_err.warning.assert_called_once_with("[RANK:0] from unknown at line 0: Test warning")
        mock_info.assert_called_once_with('Warning raised by rank 0 ! See error log for details\n', 0)

def test_abort():
    mock_logger_err = MagicMock(spec=logging.Logger)
    mock_info = MagicMock()
    mock_quit_eophis = MagicMock()
    with patch('mon_module_de_logs._logger_err', mock_logger_err), \
         patch('mon_module_de_logs.info', mock_info), \
         patch('mon_module_de_logs.quit_eophis', mock_quit_eophis):
        abort("Test error")
        assert _Logbuffer.content == ["RUN ABORTED by rank 0 see error log for details"]
        mock_logger_err.error.assert_called_once_with("[RANK:0] from unknown at line 0: Test error")
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
    assert namelist.formatted['namelist1']['var1'] == 'value1'
    assert namelist.formatted['namelist2']['var4'] == 'value4'
    assert namelist.raw == ["&namelist1", "    var1 = value1", "    var2 = value2", "/", "", "&namelist2", "    var3 = value3", "    var4 = value4", "/"]

def test_raw_content(namelist_file):
    lines = raw_content(namelist_file)
    assert lines == ["&namelist1", "    var1 = value1", "    var2 = value2", "/", "", "&namelist2", "    var3 = value3", "    var4 = value4", "/"]

def test_find(namelist_file):
    lines = raw_content(namelist_file)
    pos = find(lines, "&namelist2")
    assert pos == 6

def test_replace_line(namelist_file):
    lines = raw_content(namelist_file)
    replace_line(lines, "&namelist2a", 6)
    assert lines[6] == "&namelist2a"

def test_find_and_replace_line(namelist_file):
    lines = raw_content(namelist_file)
    find_and_replace_line(lines, "&namelist1", "&namelist1a")
    assert lines[0] == "&namelist1a"
    assert lines[1] == "    var1 = value1"

def test_find_and_replace_char(namelist_file):
    lines = raw_content(namelist_file)
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



# =========
# tunnel.py
# =========
from eophis.coupling.tunnel import Tunnel, init_oasis

def test_Tunnel():
    label = "test_tunnel"
    grids = {"grid1": (10, 10, 0, 0)}
    exchs = [{"grd": "grid1", "in": ["var1"], "out": ["var2"], "freq": 3600, "lvl": 1}]
    geo_aliases = {"var1": "VAR1_GEO", "var2": "VAR2_GEO"}
    py_aliases = {"var1": "VAR1_PY", "var2": "VAR2_PY"}

    tunnel = Tunnel(label, grids, exchs, geo_aliases, py_aliases)

    assert tunnel.label == label
    assert tunnel.grids == grids
    assert tunnel.exchs == exchs
    assert tunnel.geo_aliases == geo_aliases
    assert tunnel.py_aliases == py_aliases
    assert tunnel.local_grids == {}
    assert tunnel.arriving_list() == ["var1"]
    assert tunnel.departure_list() == ["var2"]

# ============
# namcouple.py
# ============
from eophis.coupling.namcouple import Namcouple, register_tunnels, init_namcouple

def test_Namcouple():
    infile = "test_namcouple.in"
    outfile = "test_namcouple.out"

    namcouple = Namcouple(infile, outfile)

    assert namcouple.infile == infile
    assert namcouple.outfile == outfile
    assert namcouple.tunnels == []
    assert namcouple.comp == None
    assert namcouple._Nin == 0
    assert namcouple._Nout == 0
    assert namcouple._activated == False
    assert namcouple.lines == [ '$NFIELDS', '0', '$END', '############', '$RUNTIME', '0', '$END', '############', '$NLOGPRT', '1 0', '$END', '############', '$STRINGS', '#', '$END' ]
    
def test_register_tunnels():
    configs = [
        {
            "label": "test_tunnel",
            "grids": {"grid1": (10, 10, 0, 0)},
            "exchs": [{"grd": "grid1", "in": ["var1"], "out": ["var2"], "freq": 3600, "lvl": 1}],
            "geo_aliases": {"var1": "VAR1_GEO", "var2": "VAR2_GEO"},
            "py_aliases": {"var1": "VAR1_PY", "var2": "VAR2_PY"}
        }
    ]

    infile = "test_namcouple.in"
    outfile = "test_namcouple.out"

    namcouple = Namcouple(infile, outfile)

    tunnels = register_tunnels(configs)

    assert len(tunnels) == 1
    assert tunnels[0].label == "test_tunnel"
    assert tunnels[0].grids == {"grid1": (10, 10, 0, 0)}
    assert tunnels[0].exchs == [{"grd": "grid1", "in": ["var1"], "out": ["var2"], "freq": 3600, "lvl": 1}]
    assert tunnels[0].geo_aliases == {"var1": "VAR1_GEO", "var2": "VAR2_GEO"}
    assert tunnels[0].py_aliases == {"var1": "VAR1_PY", "var2": "VAR2_PY"}

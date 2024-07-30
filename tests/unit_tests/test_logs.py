import os
import shutil
import logging
from unittest.mock import MagicMock, patch
import pytest
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
# test logs.py
# ============
from eophis.utils.logs import info, warning, abort, _Logbuffer, _logger_info, _logger_err

def test_inquire_log_files():
    assert os.path.exists("eophis.out"), "log file 'eophis.out' does not exist"
    assert os.path.exists("eophis.err"), "log file 'eophis.err' does not exist"

def test_info():
    _Logbuffer.store = False
    Paral.RANK = Paral.MASTER
    mock_logger_info = MagicMock(spec=logging.Logger)
    with patch('eophis.utils.logs._logger_info', mock_logger_info):
        info("Test message")
        mock_logger_info.info.assert_called_once_with("Test message")

def test_warning():
    caller = os.getcwd() + '/test_logs.py'
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
    caller = os.getcwd() + '/test_logs.py'
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

import eophis
from eophis import Freqs, Grids
import numpy as np
import os
import pytest

def setup_function():
    import eophis
    from eophis import Freqs, Grids

def teardown_function():
    for file_name in ["eophis.out", "eophis.err"]:
        if os.path.exists(file_name):
            os.remove(file_name)

# Test presence of log files
def check_log_files():
    assert os.path.exists("eophis.out"), "log file 'eophis.out' does not exist"
    assert os.path.exists("eophis.err"), "log file 'eophis.err' does not exist"


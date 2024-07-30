import os
import shutil
from unittest.mock import MagicMock, patch
from mpi4py import MPI
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
    if os.path.isdir("__pycache__"):
        shutil.rmtree("__pycache__")

# ==============
# test worker.py
# ==============
from eophis.utils.worker import Paral, set_local_communicator

def test_set_local_communicator():
    new_comm = MagicMock(spec=MPI.Intracomm)
    new_rank = new_comm.Get_rank()
    set_local_communicator(new_comm)
    assert Paral.EOPHIS_COMM == new_comm
    assert Paral.RANK == new_rank

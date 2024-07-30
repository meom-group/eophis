import os
import shutil
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

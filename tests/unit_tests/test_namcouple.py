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


# =================
# test namcouple.py
# =================
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
    
    # write OASIS namelist
    Paral.RANK = Paral.MASTER
    set_mode('preprod')
    write_coupling_namelist()
    assert os.path.exists("test_namcouple"), "file 'test_namcouple' has not been written"

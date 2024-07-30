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


# ================
# test namelist.py
# ================
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

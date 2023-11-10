"""
namelists.py - tools to manipulate namelist content
"""
# external modules
import f90nml
from ..utils import logs

__all__ = ['FortranNamelist']

class FortranNamelist:
    """
    This class is a wrapper to manipulate formatted Fortran namelists
    
    Attributes:
        file_path (str): path to namelist file
        formatted (f90nml.namelist.Namelist): content of the namelist file in Fortran format
        raw (list): namelist file lines
    Methods:
        _read: read namelist
        get: access namelist values
        write: write namelist in an output file
    """
    def __init__(self,file_path):
        self.file_path = file_path
        self._read(file_path)
        
    def _read(self,file_path):
        """
        Read namelist content in Fortran and raw format (list of file lines)
        
        Args:
            file_path (str): path to namelist
        """
        self.formatted = f90nml.read(file_path)
        self.raw = raw_content(file_path)

    def get(self,*labels):
        """
        Access the values of variables labels contained in namelist
        
        Args:
            labels (str): list of labels to find in namelist
        Returns:
            List of values corresponding to labels
        """
        res = { label : gr2 for gr1,gr2 in self.formatted.groups() for label in labels if label.lower() in gr1 }
        return [ res[label] for label in labels ]

    def write(self):
        """ Write namelist under Fortran format """
        outfile = self.file_path
        f90nml.write(self.nml,outfile)



def raw_content(file_path):
    """
    Read lines contained in a file
    
    Args:
        file_path (str): path to file
    Returns:
        lines (list): file lines (str)
    """
    try:
        infile = open(file_path,'r')
        lines = (infile.read()).split("\n")
        del lines[-1:]
        infile.close()
    except FileNotFoundError:
        lines = []
    return lines
        
        
def find(lines,target):
    """
    Find text inside of a read file list of lines
    
    Args:
        lines (list): list of lines
        target (str): text to find
    Returns:
        pos (int): line number containing target
    """
    return [i for i,txt in enumerate(lines) if target in txt][0]
        
        
def replace(lines,content,pos):
    """
    Replace a specified line of a read file list of lines by another
    
    Args:
        lines (list): list of lines
        content (str): replacement line content
        pos (int): line number to replace
    """
    del lines[pos]
    lines.insert(pos,content)
        
        
def find_and_replace(lines,old_txt,new_txt,offset=0):
    """
    Apply find and replace functions to a read file list of lines
    
    Args:
        lines (list): list of lines
        old_txt (str): content to replace
        new_txt (str): replacement content
        offset (int): line number offset for replacement
    """
    pos = [i for i,txt in enumerate(lines) if old_txt in txt][0]
    replace(lines,new_txt,pos+offset)
        
        
def write(lines,outfile,add_header=False):
    """
    Write list of lines in an output file
    
    Args:
        lines (list): list of lines
        outfile (str): content to replace
        add_header (bool): add "MODIFIED BY EOPHIS" to output file if True
    """
    header = '############# MODIFIED BY EOPHIS ###############'
    lines.insert(0,header) if add_header else None 
    file = open(outfile,'w')
    for l in lines:
        file.write(l+'\n')
    file.close()

"""
Tools to manipulate namelist content.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""
# external modules
import f90nml

__all__ = ['FortranNamelist']

class FortranNamelist:
    """
    This class is a wrapper to manipulate formatted Fortran namelists.
    
    Attributes
    ----------
    file_path : string
        path to namelist file
    formatted : f90nml.namelist.Namelist
        content of the namelist file in Fortran format
    raw : list( string )
        namelist file lines

    """
    def __init__(self,file_path):
        self.file_path = file_path
        self._read(file_path)
        
    def _read(self,file_path):
        """
        Reads namelist.
        
        Parameters
        ----------
        file_path : string
            path to namelist
        
        """
        self.formatted = f90nml.read(file_path)
        self.raw = raw_content(file_path)

    def get(self,*labels):
        """
        Accesses the values of variables labels contained in namelist.
        
        Parameters
        ----------
        labels : string
            list of labels to find in namelist
            
        Returns
        -------
        values : list
            List of values corresponding to labels
            
        """
        res = { label : gr2 for gr1,gr2 in self.formatted.groups() for label in labels if label.lower() in gr1 }
        return [ res[label] for label in labels ]

    def write(self):
        """ Writes namelist under Fortran format. """
        outfile = self.file_path
        f90nml.write(self.nml,outfile)


def raw_content(file_path):
    """
    Reads lines contained in a file.
    
    Parameters
    ----------
    file_path : string
        path to file
        
    Raises
    ------
    FileNotFoundError
        if file at file_path does not exist
        
    Returns
    -------
    lines : list( string )
        file lines (str), empty list if FileNotFoundError.
        
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
    Finds first text occurence inside of a read file list of lines.
    
    Parameters
    ----------
    lines : list( string )
        list of lines
    target : string
        text to find
    
    Returns
    -------
    pos : int
        line number containing target
        
    """
    return [i for i,txt in enumerate(lines) if target in txt][0]
        
        
def replace_line(lines,content,pos):
    """
    Replaces a specified line of a read file list of lines by another complete line.
    
    Parameters
    ----------
    lines : list( string )
        list of lines
    content : string
        replacement line content
    pos : int
        line number to replace
        
    """
    del lines[pos]
    lines.insert(pos,content)
        
        
def find_and_replace_line(lines,old_txt,new_txt,offset=0):
    """
    Applies find() and replace_line() to a read file list of lines.
    
    Parameters
    ----------
    lines : list( string )
        list of lines
    old_txt : string
        content to replace
    new_txt string :
        replacement content
    offset : int
        line number offset for replacement
        
    """
    pos = [i for i,txt in enumerate(lines) if old_txt in txt][0]
    replace_line(lines,new_txt,pos+offset)


def find_and_replace_char(lines,old_char,new_char):
    """
    Replaces every character chain occurence in a read file list of lines
    by another character chain, lines are saved.
    
    Parameters
    ----------
    lines : list( string )
        list of lines
    old_char : string
        character to replace
    new_char : string
        new character for replacement
        
    """
    for i,txt in enumerate(lines):
        if old_char in txt:
            lines[i] = txt.replace(old_char,new_char)
        

def write(lines,outfile,add_header=False):
    """
    Writes list of lines in an output file.
    
    Parameters
    ----------
    lines : list( string )
        list of lines
    outfile : string
        output file path
    add_header : bool
        add "MODIFIED BY EOPHIS" to output file if True
        
    """
    header = '############# MODIFIED BY EOPHIS ###############'
    lines.insert(0,header) if add_header else None 
    file = open(outfile,'w')
    for l in lines:
        file.write(l+'\n')
    file.close()

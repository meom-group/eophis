# external modules
import f90nml

__all__ = ['FortranNamelist']

class FortranNamelist:
    """
    Wrapper to manipulate formatted Fortran namelist
    """
    def __init__(self,file_path):
        self.file_path = file_path
        self._read(file_path)
        
    def _read(self,file_path):
        self.formatted = f90nml.read(file_path)
        
    def get(self,*labels):
        return [ gr2 for gr1,gr2 in self.nml.groups() for label in labels if label in gr1 ]
       
    def write(self,outfile=self.file_path):
        f90nml.write(self.nml,outfile)


"""
Tools to manipulate raw file contents
"""
def raw_content(file_path):
    infile = open(file_path,'r')
    lines = (infile.read()).split("\n")
    del lines[-1:]
    infile.close()
    return lines
        
def find(lines,target):
    return [i for i,txt in enumerate(lines) if target in txt][0]
        
def replace(lines,content,pos):
    del lines[pos]
    lines.insert(pos,content)
        
def find_and_replace(lines,old_txt,new_txt,offset=0):
    pos = [i for i,txt in enumerate(lines) if target in txt][0]
    replace(new_txt,self.pos+offset)
        
def write(lines,outfile=self.output,add_header=False):
    header = "############# MODIFIED BY EOPHIS ###############"
    lines.insert(0,header) if add_header else None
        
    file = open(self.outfile,'w')
    for l in lines:
        file.write(l+'\n')
    file.close()

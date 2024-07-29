"""
halo.py - This module contains tools to define halo cells that do not cross boundaries.
"""
# external module
import numpy as np

__all__ = []

class HaloGrid:
    """
    This class represents the halo cells of a given subdomain in a global grid. HaloGrid only knows how to identify halo cells if they do not cross the global grid boundaries. It also setup the operations to rebuild a raw field received by OASIS.
        
    Attributes
    ----------
    size : int
        number of halo cells
    global_grid : (int,int)
        global grid size for (x,y) dimensions
    local_grid : (int,int)
        subdomain local grid size for (x,y) dimension
    offset : int
        global offset of the local subdomain
        
    """
    def __init__(self, size, global_grid, local_grid, offset):
        self.size = size
        self.global_grid = global_grid
        self.local_grid = local_grid
        self.offset = offset
    
    @classmethod
    def select_type(cls, grd, fold, bnd, size, global_grid, local_grid, offset):
        """
        Returns a halo grid corresponding to local and global grid properties.
        HaloGrid states in three different types:
            1. No halo cells or halo cells do not cross global grid boundaries -- HaloGrid
            2. Halo cells do cross global grid closed/cyclic boundaries -- CyclicHalo
            3. Halo cells do cross global grid north fold boundary -- NFHalo
                
        This method may be called without instantiating a HaloGrid object.
                
        Parameters
        ----------
            grd, fold, bnd : eophis.Grid
                same as eophis.Grid attributes
            size : int
                number of halo cells in both dimensions
            global_grid, local_grid, ofset : (int,int)
                same as eophis.HaloGrid attributes
        
        """
        # Does halo grid cross boundaries ?
        cross_x0 = size - offset % global_grid[0]
        cross_x1 = size - global_grid[0] + local_grid[0] + offset % global_grid[0]
        cross_y0 = size - offset // global_grid[0]
        cross_y1 = size - global_grid[1] + local_grid[1] + offset // global_grid[0]
        
        # Select grid type for halos
        if 'fold' in bnd[1]:
            if cross_y0 > 0:
                return NFHalo(size, global_grid, local_grid, offset, set_fold_trf(grd,fold), bnd)
            elif cross_x0 > 0 or cross_x1 > 0 or cross_y1 > 0:
                return CyclicHalo(size, global_grid, local_grid, offset, bnd=(bnd[0],'close'))
            else:
                return HaloGrid(size, global_grid, local_grid, offset)
        elif cross_y0 > 0 or cross_x0 > 0 or cross_x1 > 0 or cross_y1 > 0:
            return CyclicHalo(size, global_grid, local_grid, offset, bnd)
        else:
            return HaloGrid(size, global_grid, local_grid, offset)
                
    def segment(self):
        """ Decompose non boundary-crossing halos cells into offsets/sizes couple. """
        hls_offsets = []
        hls_sizes = []
        
        # segment halos cells
        for l in range( (self.size>0)*self.local_grid[1] + 2*self.size ):
            
            # above- and below- lines or real cells
            local_offset = self.offset + self.global_grid[0] * ( l - self.size )
            if l < self.size or l >= self.local_grid[1] + self.size:
                hls_offsets.append( local_offset - self.size )
                hls_sizes.append( self.local_grid[0] + 2*self.size )
            else:
                # left
                hls_offsets.append( local_offset - self.size )
                hls_sizes.append( self.size )
                # right
                hls_offsets.append( local_offset + self.local_grid[0] )
                hls_sizes.append( self.size )
        return hls_offsets, hls_sizes
        
    def segment_side_halos(self,local_start, local_offset):
        local_offset = local_offset % self.global_grid[0]
        side_A = ( self.global_grid[0] - local_offset ) * ( (self.global_grid[0]-local_offset) < self.size )
        side_B = self.size - side_A

        if side_A > 0:
            side_offsets = [ local_offset + self.global_grid[0]*(local_start // self.global_grid[0]) , ( local_offset + self.global_grid[0]*(local_start // self.global_grid[0]) - self.global_grid[0] + side_A ) ]
            side_sizes = [ side_A , side_B ]
        else:
            side_offsets = [ local_offset + self.global_grid[0]*(local_start // self.global_grid[0]) ]
            side_sizes = [ side_B ]
        return side_offsets, side_sizes

    def rebuild(self, field_grid, full_dim=(0,0)):
        """ Rebuild a received field from OASIS into subdomain with non boundary-crossing halo cells. """
        size_x = self.local_grid[0] + 2*self.size*(1-full_dim[0])
        size_y = self.local_grid[1] + 2*self.size*(1-full_dim[1])
        size_z = field_grid.shape[1]
        if len(field_grid) == size_x*size_y:
            field_grid = field_grid.reshape(size_x,size_y,size_z,order='F')
        return field_grid

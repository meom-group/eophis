"""
halo.py - This module contains tools to define halo cells that do not cross global domain boundaries.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
    
"""
# external module
import numpy as np

__all__ = []

class HaloGrid:
    """
    This class represents the halo cells of a given subdomain in a global grid. HaloGrid only knows how to identify halo cells if they do not cross the global grid boundaries. It also configures the operations to rebuild a raw field received by OASIS.
        
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
                
    def segment(self):
        """ Decomposes non boundary-crossing halos cells into offsets/sizes couple. """
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
        """ Rebuilds a received field from OASIS into a subdomain with non boundary-crossing halo cells. """
        size_x = self.local_grid[0] + 2*self.size*(1-full_dim[0])
        size_y = self.local_grid[1] + 2*self.size*(1-full_dim[1])
        size_z = field_grid.shape[1]
        if len(field_grid) == size_x*size_y:
            field_grid = field_grid.reshape(size_x,size_y,size_z,order='F')
        return field_grid

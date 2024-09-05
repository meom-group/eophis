"""
cyclichalo.py - This module contains tools to define halo cells that do cross global domain periodic/closed boundaries.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""
# eophis modules
from ..utils import logs
from .halo import HaloGrid
# external module
import numpy as np

__all__ = []

class CyclicHalo(HaloGrid):
    """
    This class represents the halo cells of a given subdomain in a global grid. CyclicHalo only knows how to identify halo cells if they do cross the global grid closed or cyclic boundaries. It also configures the operations to rebuild a raw field received by OASIS with closed/cyclic halo cells.
    
    Attributes
    ----------
    size, global_grid, local_grid, offset : eophis.HaloGrid
        same as eophis.HaloGrid attributes
    bnd : eophis.grid
        same as eophis.Grid attributes
    shifts : (int,int)
        shift to apply to put periodic halos to correct position for (x,y) dimensions
    close : (int,int)
        index size on which set halo cells to zero for (x,y) dimensions
    full_dim : (bool,bool)
        indicates if local grid size is equal to global grid size for (x,y) dimensions
        
    """
    def __init__(self, size, global_grid, local_grid, offset, bnd=('close','close')):
        super().__init__(size, global_grid, local_grid, offset)
    
        # grid info
        self.full_dim = ( local_grid[0] == global_grid[0] , local_grid[1] == global_grid[1] )
    
        # compute shifts
        cross_x0 = size - offset % global_grid[0]
        cross_x0 = cross_x0 * ( cross_x0 > 0 ) * (1-self.full_dim[0])
        cross_x1 = size - global_grid[0] + local_grid[0] + offset % global_grid[0]
        cross_x1 = - cross_x1 * ( cross_x1 > 0 ) * (1-self.full_dim[0])
        
        cross_y0 = size - offset // global_grid[0]
        cross_y0 = cross_y0 * ( cross_y0 > 0 ) * (1-self.full_dim[1])
        cross_y1 = size - global_grid[1] + local_grid[1] + offset // global_grid[0]
        cross_y1 = - cross_y1 * ( cross_y1 > 0 ) * (1-self.full_dim[1])

        # rebuild instructions
        self.shifts = ( max(cross_x0,cross_x1,key=abs) , max(cross_y0,cross_y1,key=abs) )
        self.close = ( (bnd[0] == 'close') * (self.shifts[0]+self.full_dim[0]*self.size) , (bnd[1] == 'close') * (self.shifts[1]+self.full_dim[1]*self.size) )
    
        # check size compatibility
        nlines = local_grid[1] + 2*size * (1-self.full_dim[1])
        ncol = local_grid[0] + 2*size * (1-self.full_dim[0])
        if size < 0:
            logs.abort(f'Halo size cannot be negative !!!')
        if nlines > global_grid[1] or self.full_dim[1] and (local_grid[1] + 2*size) > 2*global_grid[1]:
            logs.abort(f'Halo size {size} is too big for x dimension {global_grid[1]}')
        if ncol > global_grid[0] or self.full_dim[0] and (local_grid[0] + 2*size) > 2*global_grid[0]:
            logs.abort(f'Halo size {size} is too big for y dimension {global_grid[0]}')
    
    def segment(self):
        """ Decomposes close/cyclic boundary-crossing halo cells into offsets/sizes couple. """
        hls_offsets = []
        hls_sizes = []
    
        start_line = 0 + self.size*self.full_dim[1]
        end_line = self.local_grid[1] + self.size + self.size*(1-self.full_dim[1])
    
        # segment halos cells
        for l in range( start_line , end_line ):
            start = self.offset + self.global_grid[0] * ( l - self.size )
            start = start % (self.global_grid[0]*self.global_grid[1])
            
            # above- and below- intern lines
            if l < self.size or l >= self.local_grid[1] + self.size:
                hls_offsets.append( start )
                hls_sizes.append( self.local_grid[0] )
            
            # extremities
            if not self.full_dim[0]:
                # left
                local_offset = ( start % self.global_grid[0] - self.size )
                off, siz = super().segment_side_halos(start,local_offset)
                hls_offsets += off
                hls_sizes += siz
                
                # right
                local_offset = ( start % self.global_grid[0] + self.local_grid[0] )
                off, siz = super().segment_side_halos(start,local_offset)
                hls_offsets += off
                hls_sizes += siz
        return hls_offsets, hls_sizes
    
    def rebuild(self, field_grid):
        """ Rebuilds a received field from OASIS into subdomain with close/cyclic boundary-crossing halo cells. """
        field_grid = super().rebuild(field_grid,self.full_dim)
        field_grid = np.roll(field_grid,self.shifts[0],axis=0)
        field_grid = np.roll(field_grid,self.shifts[1],axis=1)
        field_grid = self.fill_boundary_halos(field_grid)
        return field_grid
    
    def fill_boundary_halos(self,field_grid):
        """ Creates received field halo cells if global grid size is contained within the subdomain, applies closing condition. """
        # duplicate opposite boundary cells for periodicity
        if self.full_dim[0]:
            left = field_grid[:self.size,:,:]
            right = field_grid[-self.size:,:,:]
            field_grid = np.vstack( (right,field_grid) )
            field_grid = np.vstack( (field_grid,left) )
        if self.full_dim[1]:
            up = field_grid[:,:self.size,:]
            bottom = field_grid[:,-self.size:,:]
            field_grid = np.hstack( (bottom,field_grid) )
            field_grid = np.hstack( (field_grid,up) )
            
        # closing
        if self.close[0] > 0 or self.full_dim[0] and self.close[0] != 0:
            field_grid[:self.close[0],:,:] = 0.0
        if self.close[0] < 0 or self.full_dim[0] and self.close[0] != 0:
            field_grid[-abs(self.close[0]):,:,:] = 0.0
        if self.close[1] > 0 or self.full_dim[1] and self.close[1] != 0:
            field_grid[:,:self.close[1],:] = 0.0
        if self.close[1] < 0 or self.full_dim[1] and self.close[1] != 0:
            field_grid[:,-abs(self.close[1]):,:] = 0.0
        return field_grid

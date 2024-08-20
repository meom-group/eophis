"""
nfhalo.py - This module contains tools to define halo cells that do cross North Fold boundary.
"""
# eophis modules
from ..utils import logs
from .halo import HaloGrid
from .offsiz import grid_to_offsets_sizes, list_to_slices, set_fold_trf
# external module
import numpy as np

__all__ = []

class NFHalo(HaloGrid):
    """
    This class represents the halo cells of a given subdomain in a global grid. NFHalo only knows how to identify halo cells if they do cross the global grid north fold boundary. It also setup the operations to rebuild a raw field received by OASIS with north folded halo cells.
    
    Attributes
    ----------
    size, global_grid, local_grid, offset : eophis.HaloGrid
        same as eophis.HaloGrid attributes
    bnd : eophis.grid
        same as eophis.Grid attributes
    fold_param : list(int,int,int)
        Folding parameters, given by eophis.set_fold_trf.()
    shifts : (int,int)
        shift to apply to put periodic halos to correct position for (x,y) dimensions
    close : int
        index size on which set halo cells to zero for x dimensions
    full_dim : (bool,bool)
        indicates if local grid size is equal to global grid size for (x,y) dimensions
    _moves : numpy.ndarray
        elements in received grid to extract to build folded halo cells
    _copies : numpy.ndarray
        elements in received grid to copy to build folded halo cells

    """
    def __init__(self, size, global_grid, local_grid, offset, fold_param=None, bnd=('close','nfold')):
        super().__init__(size, global_grid, local_grid, offset)
        
        # grid info
        self.fold_param = fold_param if fold_param is not None else set_fold_param('T','T')
        self.full_dim = ( local_grid[0] == global_grid[0] , local_grid[1] == global_grid[1] )

        # compute shifts
        cross_x0 = size - offset % global_grid[0]
        cross_x0 = cross_x0 * ( cross_x0 > 0 ) * (1-self.full_dim[0])
        cross_x1 = size - global_grid[0] + local_grid[0] + offset % global_grid[0]
        cross_x1 = - cross_x1 * ( cross_x1 > 0 ) * (1-self.full_dim[0])
        
        # rebuild instructions
        self.shifts = ( max(cross_x0,cross_x1,key=abs) , size - offset // global_grid[0] )
        self.close = (bnd[0] == 'close') * ( self.shifts[0]+self.full_dim[0]*self.size )
        self._fold_bnd = 0
        self._moves = []
        self._copies = []

        # check size compatibility
        nlines = local_grid[1] + 2*size * (1-self.full_dim[1]) + size*(1-self.full_dim[0])*self.full_dim[1]
        ncol = local_grid[0] + 2*size * (1-self.full_dim[0])
        if size < 0:
            logs.abort(f'Halo size cannot be negative !!!')
        if nlines > (global_grid[1] + self.size) or self.full_dim[1] and (local_grid[1] + 2*size) > 2*global_grid[1]:
            logs.abort(f'Halo size {size} is too big for x dimension {global_grid[1]}')
        if ncol > global_grid[0] or self.full_dim[0] and (local_grid[0] + 2*size) > 2*global_grid[0]:
            logs.abort(f'Halo size {size} is too big for y dimension {global_grid[0]}')
        
    def segment(self):
        """ Decompose North Fold boundary-crossing halo cells into offsets/sizes couple. """
        hls_offsets = [[],[]]
        hls_sizes = [[],[]]
        
        start_line = 0 + self.size * ( self.full_dim[0] and self.full_dim[1] )
        end_line = self.local_grid[1] + self.size + self.size*(1-self.full_dim[1])

        # segment halos cells
        for l in range( start_line , end_line ):
            start = self.offset + self.global_grid[0] * ( l - self.size )
                                    
            # above- and below- intern lines
            if l < self.shifts[1]:
                # folded halos
                start += self.global_grid[0] * (self.shifts[1]-l) - self.fold_param[1] + self.local_grid[0]
                start = start % self.global_grid[0] - self.global_grid[0] * ( self.fold_param[0] + (self.shifts[1]-l) )
                start += self.global_grid[0] * (abs(start)%self.global_grid[0] == 0)
                start = abs(start)
                
                off, siz = self.segment_intern_fold(start)
                hls_offsets[1] += off
                hls_sizes[1] += siz
            else:
                # regular halos (and real cells for rebuild instructions)
                start = start % (self.global_grid[0]*self.global_grid[1])
                hls_offsets[0].append( start )
                hls_sizes[0].append( self.local_grid[0] )
            
            # extremities
            if not self.full_dim[0]:
                hls = 1 if l < self.shifts[1] else 0
                # left
                local_offset = ( start % self.global_grid[0] - self.size )
                off, siz = super().segment_side_halos(start,local_offset)
                hls_offsets[hls] += off
                hls_sizes[hls] += siz

                # right
                local_offset = ( start % self.global_grid[0] + self.local_grid[0] )
                off, siz = super().segment_side_halos(start,local_offset)
                hls_offsets[hls] += off
                hls_sizes[hls] += siz
                
        # set rebuild instructions from segmentation
        if self.full_dim[0] and self.full_dim[1]:
            return hls_offsets[0], hls_sizes[0]
        else:
            return self.rebuild_instructions( hls_offsets, hls_sizes )
    
    def segment_intern_fold(self, local_start):
        avail_size = self.local_grid[0]
        inner_size = self.global_grid[0] - local_start % self.global_grid[0]
        side_A = inner_size * ( inner_size < avail_size )
        side_B = avail_size - side_A
        
        if side_A > 0:
            fold_offsets = [ local_start , local_start - self.global_grid[0] + side_A ]
            fold_sizes = [ side_A , side_B ]
        else:
            fold_offsets = [ local_start ]
            fold_sizes = [ side_B ]
        return fold_offsets, fold_sizes
    
    def rebuild_instructions(self, offsets, sizes):
        """ Identify operations required to build the folded halo cells from a received field. """
        # folded / regular partitions
        folded_grid = np.concatenate([np.arange(off, off + size) + 1 for off, size in zip(offsets[1], sizes[1])])
        right_grid = np.concatenate([np.arange(off, off + size) + 1 for off, size in zip(offsets[0], sizes[0])])

        # check if folded halos cross first dimension boundary
        self._fold_bnd = ( np.min(folded_grid) % self.global_grid[0] == 1 ) and ( np.max(folded_grid) % self.global_grid[0] == 0 )

        # build artificial oasis partition
        offsets = np.concatenate(offsets)
        sizes = np.concatenate(sizes)
        oasis_grid = np.concatenate([np.arange(off, off + size) + 1 for off, size in zip(offsets, sizes)])

        # remove duplicates
        oasis_grid = np.unique(oasis_grid)

        # convert back to offsets / sizes
        oasis_grid = np.sort(oasis_grid)
        offsets, sizes = grid_to_offsets_sizes(oasis_grid)

        # elements in oasis grid to extract to build folded grid
        non_common_idx = np.where( ~np.isin(folded_grid, right_grid) )[0]
        non_common_elt = folded_grid[non_common_idx]
        mv_idx = np.where( np.isin(oasis_grid, non_common_elt) )[0]

        # elements in oasis grid to copy to build folded grid
        cp_idx = np.where( np.isin(oasis_grid, folded_grid) & np.isin(oasis_grid, right_grid) )[0]
        cp_idx = np.hstack((cp_idx,mv_idx))
        cp_idx = np.sort(cp_idx)

        # reduce index list to slices
        self._copies = list_to_slices(cp_idx)
        self._moves = list_to_slices(mv_idx)
        return offsets, sizes
    
    def rebuild(self, field_grid):
        """ Rebuild a received field from OASIS into subdomain with North Fold boundary-crossing halo cells. """
        # make halos grid
        if len(self._copies) != 0:
            S_cp = self._copies[:,0]
            E_cp = self._copies[:,1]
            folded_grid = np.concatenate([ field_grid[S_cp[i]:E_cp[i],:] for i in range(len(S_cp)) ])
            folded_grid = self.rebuild_halos(folded_grid)

        # remove halos to make real grid
        if len(self._moves) != 0:
            S_rm = self._moves[:,0]
            E_rm = self._moves[:,1]
            mask = np.ones(len(field_grid), dtype=bool)
            for i in range(len(S_rm)):
                mask[S_rm[i]:E_rm[i]] = False
            field_grid = field_grid[mask,:]
            
        # rebuild real grid
        size_x = self.local_grid[0] + 2*self.size * (1-self.full_dim[0])
        size_y = self.local_grid[1] + (2*self.size - self.shifts[1]) * (1-self.full_dim[1])
        size_z = field_grid.shape[1]
        field_grid = field_grid.reshape(size_x,size_y,size_z,order='F')
        field_grid = np.roll(field_grid,self.shifts[0],axis=0)

        # merge grids
        if not ( self.full_dim[0] and self.full_dim[1] ):
            field_grid = np.hstack( (folded_grid,field_grid) )
        
        # boundary treatment
        field_grid = self.fill_boundary_halos(field_grid)
        return field_grid
    
    def rebuild_halos(self, halos_grid):
        """ Rebuild the North Fold halo cells extracted from received field. """
        size_z = halos_grid.shape[1]
        halos_grid = halos_grid.reshape( len(halos_grid)//self.shifts[1], self.shifts[1], size_z ,order='F' )
        halos_grid = np.flip(halos_grid , axis=(0,1))
        halos_grid = np.roll(halos_grid, (self.shifts[0]+self.fold_param[1])*self._fold_bnd, axis=0)
        return halos_grid
    
    def fill_boundary_halos(self,field_grid):
        """ Creates received field halo cells if global grid size is contained within the subdomain, apply closing condition. """
        # build folded halos from whole grid
        if self.full_dim[0] and self.full_dim[1]:
            folded_halos = field_grid[ :, self.fold_param[0] : self.fold_param[0]+self.size , : ].copy()
            folded_halos = np.flip(folded_halos,axis=(0,1))
            folded_halos= np.roll( folded_halos , self.fold_param[1] , 0 )
            field_grid = np.hstack( (folded_halos,field_grid) )
            
        # build cyclic halos from whole grid
        if self.full_dim[0]:
            left = field_grid[:self.size,:,:]
            right = field_grid[-self.size:,:,:]
            field_grid = np.vstack( (right,field_grid) )
            field_grid = np.vstack( (field_grid,left) )
        if self.full_dim[1]:
            up = np.zeros_like( field_grid[:,:self.size,:] )
            field_grid = np.hstack( (field_grid,up) )
            
        # closing
        if self.close > 0 or self.full_dim[0] and self.close != 0:
            field_grid[:self.close,:,:] = 0.0
        if self.close < 0 or self.full_dim[0] and self.close != 0:
            field_grid[-abs(self.close):,:,:] = 0.0
        return field_grid

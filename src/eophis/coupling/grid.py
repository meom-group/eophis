"""
grid.py - This module contains tools for grid definition and parallel decomposition
"""
# eophis modules
from ..utils import logs
# external module
import numpy as np

__all__ = ['Grids']

class Grids:
    """
    This class contains pre-defined commonly used earth grids for coupled run.
    Grids is a dict which keys are and refer to:
        npts : (int,int):  number of longitude and latitude points, respectively
        halos : (int): grid halos size, same in both x and y direction
        bnd : (int,int): boundary conditions in x and y direction, needed to fill boundary halos.
                         --> close (0), cyclic-periodic (1) or northfold (2)
    
    Attributes:
        eORCA05 (eophis.Grids): size = (720,603), halos = 1, bnd = (2,1)
        eORCA025 (eophis.Grids): size = (1442,1207), halos = 1, bnd = (2,1)
    """
    eORCA05 =  {'npts' : (720,603)   , 'halos' : 1, 'bnd' : (2,1)}
    eORCA025 = {'npts' : (1442,1207) , 'halos' : 1, 'bnd' : (2,1)}


def make_subdomains(nx, ny, ncpu):
    """
    This function finds the best subdomain decomposition from global grid size and number of cpus
    
    Args:
        nx,ny (int): grid global size in x and y directions, respectively
        ncpu (int): number of cpu
    Raises:
        Abort if global grid size is lower than cpu size
    Returns:
        rankx (int,...): list of subdomains sizes in x lines
        ranky (int,...): list of subdomains sizes in y columns
    """
    # size compatibility
    if nx*ny < ncpu:
        logs.abort(f'Grid size ({nx,ny}) too small for CPU number {ncpu}')
    
    # init
    target = max(nx/ny , ny/nx)
    diff0 = float('inf')
    
    # find integers px,py such as px*py = ncpu and px/py --> nx/ny
    for i in range(1, int(ncpu**0.5) + 1):
        for j in range(i, ncpu // i + 1):
            if i*j == ncpu:
                diff = abs( j / i - target )
                if diff < diff0:
                    diff0 = diff
                    px = j if nx >= ny else i
                    py = i if nx >= ny else j
                    
    # decompose grid size over subdomains
    rankx = tuple( 1 + nx // px if i < nx % px else nx // px for i in range(px) )
    ranky = tuple( 1 + ny // py if i < ny % py else ny // py for i in range(py) )
    return rankx, ranky


def make_segments(global_size_x, global_size_y, halos, loc_sizes_x, loc_sizes_y, domid):
    """
    This function decomposes a subdomain into several one-dimension segments containing halos / non-halos parts.
    
    Args:
        global_size_x (int): grid global size in x direction
        global_size_y (int): grid global size in y direction
        halos (int): halos size, same in both x and y direction
        loc_sizes_x (int,...): list of sudomains sizes in x lines
        loc_sizes_y (int,...): list of sudomains sizes in y columns
        domid (int): subdomain index to segment
    Raises:
        Abort if halos size is negative
        Abort if halos size make them to overlap themselves
    Returns
        seg_offsets (int,...): list of segments offsets
        seg_sizes (int,...): list of segments sizes
        shifts (int,int): shifts to apply in x,y direction for grid reconstruction
        full_dim (int,int): global size is locally contained (1) or not (0) in (x,y) directions
    """
    # init
    shifts = [0,0]
    seg_sizes = []
    seg_offsets = []

    # local grid dimensions
    isub = domid % len(loc_sizes_x) 
    jsub = domid // len(loc_sizes_x)
    size_x = loc_sizes_x[isub] 
    size_y = loc_sizes_y[jsub]
    global_offset = sum(loc_sizes_y[0:jsub]) * global_size_x + sum(loc_sizes_x[0:isub])

    # no need to create halos segment and shift value if global size locally contained
    full_dim = ( size_x == global_size_x , size_y == global_size_y )

    # number of subdomain lines and columns to segment
    nlines = size_y + 2*halos * (1-full_dim[1])
    ncol = size_x + 2*halos * (1-full_dim[0]) 

    # check sizes compatibility
    if halos < 0:
        logs.abort('Halos size cannot be negative')
    if nlines > global_size_y or full_dim[1] and (size_y + 2*halos) > 2*global_size_y:
        logs.abort(f'Halos size {halos} too big for lat dimension {global_size_y}')
    if ncol > global_size_x or full_dim[0] and (size_x + 2*halos) > 2*global_size_x:
        logs.abort(f'Halos size {halos} too big for lon dimension {global_size_x}')

    # segmentation
    for l in range(nlines):
        # subdomain line
        start = global_offset + global_size_x * ( l - halos*(1-full_dim[1]) )
        if start < 0:
            shifts[1] = max( abs(start//global_size_x) , shifts[1] )
        if start >= global_size_x*global_size_y:
            shifts[1] = min( -(start//global_size_x-global_size_y+1) , shifts[1] )
        start = start % (global_size_x*global_size_y)
        
        # halos segments: left/right extremities
        if not full_dim[0] and halos > 0:
            for sd in ('left','right'):
                if sd == 'left':
                    offset = start % global_size_x - halos
                    if offset < 0:
                        shifts[0] = abs(offset)
                        offset += global_size_x
                if sd == 'right':
                    offset = start % global_size_x + size_x
                    if offset >= global_size_x:
                        shifts[0] = - halos + ( global_size_x-offset ) * ( (global_size_x-offset) < halos )
                        offset -= global_size_x

                # split segment if it crosses a boundary
                side_A = ( global_size_x-offset ) * ( (global_size_x-offset) < halos )
                side_B = halos - side_A

                if side_A > 0:
                    seg_offsets += [ offset + global_size_x*(start // global_size_x) , offset + global_size_x*(start // global_size_x - 1) + side_A ]
                    seg_sizes += [ side_A , side_B ]
                else:
                    seg_offsets += [ offset + global_size_x*(start // global_size_x) ]
                    seg_sizes += [ side_B ]
        
        # non-halos segments
        seg_offsets.append(start)
        seg_sizes.append(size_x)

    # re-arange by increasing offset values
    combined_res = list( zip(seg_offsets,seg_sizes) )
    sorted_res = sorted(combined_res, key=lambda x: x[0])
    seg_offsets, seg_sizes = zip(*sorted_res)
    return seg_offsets, seg_sizes, shifts, full_dim


def fill_boundary_halos(field_grid, halos=0, shifts=(0,0), full_dim=(0,0), bnd=(0,0)):
    """
    This function creates periodic halos for a field whose global grid size is contained within the subdomain.
    Then it sets boundary halos values in accordance with boundary conditions

    Args:
        field_grid (numpy.ndarray): input grid on which create halos
        halos (int): halos size to build
        full_dim (int,int): global size is locally contained (1) or not (0) in (x,y) directions
        bnd (int,int): boundary conditions in x,y directions
    Returns:
        field_grid (numpy.ndarray): modified input grid
    """
    if halos != 0:
        # duplicate opposite boundary cells for periodicity
        if full_dim[1]:
            left = field_grid[:,:halos,:]
            right = field_grid[:,-halos:,:]
            field_grid = np.hstack( (right,field_grid) )
            field_grid = np.hstack( (field_grid,left) )
        if full_dim[0]:
            up = field_grid[:halos,:,:]
            bottom = field_grid[-halos:,:,:]
            field_grid = np.vstack( (bottom,field_grid) )
            field_grid = np.vstack( (field_grid,up) )
            
        # closing
        close = ( (1-close[0]) * (shifts[0]+full_dim[0]*halos) , (1-close[1]) * (shifts[1]+full_dim[1]*halos) )
        
        if close[0] > 0 or full_dim[0] and close[0] != 0:
            field_grid[:close[0],:,:] = 0.0
        if close[0] < 0 or full_dim[0] and close[0] != 0:
            field_grid[-abs(close[0]):,:,:] = 0.0
        if close[1] > 0 or full_dim[1] and close[1] != 0:
            field_grid[:,:close[1],:] = 0.0
        if close[1] < 0 or full_dim[1] and close[1] != 0:
            field_grid[:,-abs(close[1]):,:] = 0.0
            
    return field_grid

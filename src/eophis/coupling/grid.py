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
    Grid is a tuple containing:
        nlon (int): number of longitude points
        nlat (int): number of latitude points
        halos (int): number of grid halos
        regional (bool): global grid (False) or regional (True), needed to fill boundary halos
    
    Attributes:
        eORCA05 (tuple): (nlon = 720, nlat = 603, halos = 1, regional = 0)
        eORCA025 (tuple): (nlon = 1440, nlat = 1206, halos = 1, regional = 0)
    """
    eORCA05 = (720,603,1,0)
    eORCA025 = (1442,1207,1,0)


def make_subdomains(nx,ny,ncpu):
    """
    This function finds the best subdomain decomposition from global grid size and number of cpus
    
    Args:
        nx,ny (int): grid global size in x and y directions, respectively
        ncpu (int): number of cpu
    Raises:
        Abort if global grid size is lower than cpu size
    Returns:
        rankx (tuple): grid size for each subdomains in x direction
        ranky (tuple): grid size for each subdomains in y direction
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


def make_segments(global_offset,halos,size_x,global_size_x,size_y,global_size_y):
    """
    This function decomposes a subdomain into several one-dimension segments containing halos / non-halos parts.
    
    Args:
        global_offset (int): subdomain global offset of its upper left corner (without halos)
        halos (int): halos size, same in both x and y direction
        size_x (int): subdomain size in x direction
        global_size_x (int): grid global size in x direction
        size_y (int): subdomain size in y direction
        global_size_y (int): subdomain size in y direction
    Raises:
        Abort if halos size make them to overlap themselves
        Abort if halos size is negative
    Returns
        offsets (tuple): list of segments offsets
        sizes (tuple): list of segments sizes
    """
    # no need to create halos segments if global size is locally contained
    periodic = ( size_x == global_size_x , size_y == global_size_y )

    # number of subdomain lines and columns to segment
    nlines = size_y + 2*halos * (1-periodic[1])
    ncol = size_x + 2*halos * (1-periodic[0])
    
    if halos < 0:
        logs.abort('Halos size cannot be negative')
    if nlines > global_size_y:
        logs.abort(f'Halos size {halos} too big for lat dimension {global_size_y}')
    if ncol > global_size_x:
        logs.abort(f'Halos size {halos} too big for lon dimension {global_size_x}')
    
    offsets = []
    sizes = []
    for l in range(nlines):
        # get subdomain line
        start = global_offset + global_size_x * ( l - halos*(1-periodic[1]) )
        start = start % (global_size_x*global_size_y)
        
        # segment 1 : left-side halos
        if not periodic[0]:
            offset = start - halos
            if start % global_size_x == 0:
                offset += global_size_x
            offsets.append(offset)
            sizes.append(halos)
        
        # segment 2 : non-halos
        offsets.append(start)
        sizes.append(rankx[isub])
        
        # segment 3 : right-side halos
        if not periodic[0]:
            offset = start + size_x
            if offset % global_size_x == 0:
                offset -= global_size_x
            offsets.append(offset)
            sizes.append(halos)

    # arange by increasing offset values
    combined_res = list( zip(offsets,sizes) )
    sorted_res = sorted(combined, key=lambda x: x[0])
    offsets, sizes = zip(*sorted_list)
    return offsets, sizes


def fill_boundary_halos(field_grid,halos,periodic=(1,1),bnd=(0,0)):
    """
    This function creates boundary halos for a field whose global grid size is contained within the subdomain.
    If asked, copy real boundary values in boundary halos (mirroring) - for regional grids.
    
    Args:
        field_grid (numpy.ndarray): grid on which create halos
        halos (int): halos size to build
        periodic (int,int): indicates if global size is locally contained (1) or not (0) in (x,y) directions
        bnd (int,int): boundary type for mirroring in (x,y) direction --> 1: left/top side, -1: right/bottom side, 0: no mirroring
    """
    if halos != 0:
        # duplicate opposite boundary cells for periodicity
        if periodic[0]:
            left = field_grid[:,:halos]
            right = field_grid[:,-halos:]
            field_grid = np.hstack( (left,field_grid) )
            field_grid = np.hstack( (field_grid,right) )
        if periodic[1]:
            up = field_grid[-halos:,:]
            bottom = field_grid[:halos,:]
            field_grid = np.vstack( (up,field_grid) )
            field_grid = np.vstack( (field_grid,bottom) )
        # mirroring
        if bndx == 1:
            field_grid[0,:,:] = field_grid[1,:,:]
        if bndx == -1:
            field_grid[-1,:,:] = field_grid[-2,:,:]
        if bndy == 1:
            field_grid[:,0,:] = field_grid[:,1,:]
        if bndy == -1:
            field_grid[:,-1,:] = field_grid[:,-2,:]

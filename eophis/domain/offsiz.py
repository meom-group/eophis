"""
offsiz.py - Miscellaneous tools to manipulate cells segments represented by an offsets/sizes couple.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""
# external module
import numpy as np

__all__ = []

def set_fold_trf(grd, fold_point):
    """ Returns parameters for NorthFold halo configuration in accordance with grid type and folding point. """
    trf_T = { 'T' : [1,1,0] , 'U' : [1,0,0] , 'V' : [2,1,0] , 'F' : [2,0,0] }
    trf_F = { 'T' : [0,0,0] , 'U' : [0,-1,0] , 'V' : [1,0,0] , 'F' : [1,-1,0] }
    trfs = { 'T' : trf_T , 'F' : trf_F }
    return trfs[fold_point][grd]


def list_to_slices(idx):
    """
    Reduces a list of integers into couples of numbers representing the start and the end of a continuous integer segment.
    
    Parameters
    ----------
        idx : list(int)
            list to reduce
    Returns
    -------
        bounds : numpy.ndarray
            start-end couples of each continuous segments
    
    """
    # return empty array if no indexes
    if len(idx) == 0:
        return np.array([])
    
    # split continuous sections
    disc_idx = np.where( np.diff(idx) != 1 )[0] + 1
    sections = np.split(idx,disc_idx)

    # sections bounds
    bounds = [ (section[0], section[-1] + 1) for section in sections ]
    return np.array(bounds)


def grid_to_offsets_sizes(grid):
    """ Transforms a list of indexed cells to a couple offsets/sizes lists (for OASIS). """
    # find discontinuities positions
    disc_idx = np.where( np.diff(grid) != 1 )[0] + 1
    
    # compute offsets
    offsets = grid[disc_idx] - 1
    offsets = np.insert(offsets,0,grid[0]-1)
    
    # sizes between two discontinuities
    sizes = np.diff(np.concatenate(([0], disc_idx, [len(grid)])))
    
    return offsets.tolist(), sizes.tolist()


def clean_for_oasis(offsets, sizes):
    """ Rearranges contents of an offsets/sizes couple to remove duplicates and sort indexes in increasing order. """
    # build artificial oasis partition
    grid = np.concatenate([np.arange(off, off + size) + 1 for off, size in zip(offsets, sizes)])

    # remove duplicates
    grid = np.unique(grid)
    
    # sort and convert back to offsets / sizes
    grid = np.sort(grid)
    return grid_to_offsets_sizes(grid)

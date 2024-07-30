"""
grid.py - This module contains tools for grid definition and parallel decomposition.
"""
# eophis modules
from ..utils import logs
from .offsiz import clean_for_oasis 
# external module
import numpy as np

__all__ = ['Domains']

class Domains:
    """
    This class contains pre-defined Grids.
    
    Attributes
    ----------
    demo (eophis.Grids): npts = (720,603), halos = 0, bnd = ('close','close'), folding = (T,T)
    eORCA05 (eophis.Grids): npts = (720,603), halos = 1, bnd = ('cyclic','NFold'), folding = (T,T)
    eORCA025 (eophis.Grids): npts = (1442,1207), halos = 1, bnd = ('cyclic','NFold'), folding = (T,T)
    
    Notes
    ------
    Domains is a dict which keys are and refer to:
        npts : (int,int)
            number of longitude and latitude points, respectively
        halos : int
            grid halos size
        bnd : (str,str)
            boundary conditions in east-west and north-south directions
        folding : (str,str)
            grid and folding type, respectively

    """
    demo    =  {'npts' : (720,603)   , 'halos' : 0, 'bnd' : ('close','close'), 'folding' : ('T','T')}
    eORCA05 =  {'npts' : (720,603)   , 'halos' : 1, 'bnd' : ('cyclic','NFold'), 'folding' : ('T','T')}
    eORCA025 = {'npts' : (1440,1206) , 'halos' : 1, 'bnd' : ('cyclic','NFold'), 'folding' : ('T','T')}



class Grid:
    """
    This class represents the grid on which fields can be discretized and exchanged. Fields are usually scattered among their executing processes and OASIS needs to know the local grid decomposition to perform optimized partition-to-partition communications.
    The class provides methods to decompose a global grid in several subdomains, identify the subdomain on which fields will be exchanged, and generate informations required by OASIS to setup communications.
    
    The local grid representing the subdomain may be divided in two parts:
        1. "real cells": cells strictly contained in the subdomain
        2. "halo cells": potential cells outside the subdomain containing neighbouring values
        
    Grid can only identify real cells. Halo cells depend on the subdomain position within global grid, halo size and boundary conditions. Thus, Grid contains a HaloGrid object to identify and configure halo cells in accordance with global and local grid properties.
    
    Sending arrays only contain real cells while receiving arrays also contain halo cells. Because of the complexity of halo definition and OASIS design, arrays received from OASIS are in a raw format that does not represent the subdomain. Grid methods can generate correctly shaped empty arrays for OASIS receptions and rebuild them into awaited subdomain shape. Grid is also able to convert a reshaped received array into a sending-shaped array.
    
    Third dimension z is not manipulated by Grid since OASIS considers that exchanging a 3D field is like communicating "nz" times on the same 2D partition.
    
    Attributes
    ----------
    label : string
        Grid name
    nx : int
        global grid size for x dimension
    ny : int
        global grid size for y dimension
    halo_size : int
        number of halo cells in both dimensions
    bnd : (string,string)
        grid boundary conditions for x and y dimensions, respectively. Used to set values of boundary-crossing halo cells
        'close' : zero, 'cyclic' : periodic, 'NFold' : North Fold
    grd : string
        grid type (T,U,V,F) for Fold boundary condition
    fold : string
        folding point (T,F) for Fold boundary condition
    subdom : int
        ID of the subdomain for which the Grid is configured
    loc_size : (int,int)
        local subdomain grid size (with halos) for which the Grid is configured
    _global_offset : int
        offset of the local subdomain within the global grid
    halos : eophis.HaloGrid
        subdomain halo grid for which the Grid is configured
    _oasis_size : int
        number of cells received by OASIS for the two first dimensions
        
    """
    def __init__(self, label, nx, ny, halo_size=0, bnd=('close','close'), grd='T', fold='T'):
        # global grid attributes
        self.label = label
        self.size = (nx,ny)
        self.halo_size = halo_size
        self.bnd = ( bnd[0].lower() , bnd[1].lower() )
        self.fold = fold.upper()
        self.grd = grd.upper()
        
        # local grid attributes
        self.subdom = None
        self.loc_size = None
        self.halos = None
        self._global_offset = 0
        self._oasis_size = 0
        
        # check arguments
        if 'fold' in self.bnd[0]:
            logs.abort(f'Grid {label}: Fold condition not implemented for x dimension')
        elif 'close' not in self.bnd[0] and 'cyclic' not in self.bnd[0]:
            logs.warning(f'Grid {label}: unrecognized x dimension boundary condition, set to close by default')
            self.bnd[0] = 'close'

        if 'fold' in self.bnd[1]:
            if 'fold' in self.bnd[0]:
                logs.abort(f'Grid {label}: Fold condition on both x,y dimensions impossible')
            if self.fold != 'T' and self.fold != 'F':
                logs.abort(f'Grid {label}: Folding point {fold} not supported')
            if self.grd != 'T' and grd != 'U' and self.grd != 'V' and self.grd != 'F':
                logs.abort(f'Grid {label}: Grid type {grd} not supported')
        elif 'close' not in self.bnd[1] and 'cyclic' not in self.bnd[1]:
            logs.abort(f'Grid {label}: unrecognized y dimension boundary condition, set to close by default')
            self.bnd[1] = 'close'
        
        # print some infos
        logs.info(f'      Grid {label} registered ')
        logs.info(f'        Global size: {nx,ny}')
        logs.info(f'        Boundary conditions: {self.bnd[0],self.bnd[1]}')
        if 'fold' in self.bnd[1]:
            logs.info(f'      Grid Type, Folding Point: {self.grd,self.fold}')
                
    def decompose(self,nsub):
        """
        Find the best decomposition of global grid for a given number of subdomains.
        
        Parameters
        ----------
        nsub : int
            number of subdomains for decomposition
            
        Returns
        -------
        rankx : tuple( int )
            grid size for each subdomains in x direction
        ranky : tuple( int )
            grid size for each subdomains in y direction
            
        """
        # init
        nx = self.size[0]
        ny = self.size[1]
        target = max(nx/ny , ny/nx)
        diff0 = float('inf')
    
        # find integers px,py such as px*py = ncpu and px/py --> nx/ny
        for i in range(1, int(nsub**0.5) + 1):
            for j in range(i, nsub // i + 1):
                if i*j == nsub:
                    diff = abs( j / i - target )
                    if diff < diff0:
                        diff0 = diff
                        px = j if nx >= ny else i
                        py = i if nx >= ny else j
                    
        # spread grid size over subdomains
        rankx = tuple( 1 + nx // px if i < nx % px else nx // px for i in range(px) )
        ranky = tuple( 1 + ny // py if i < ny % py else ny // py for i in range(py) )

        # check size compatibility
        if nx*ny < nsub:
            logs.abort(f'Grid {self.label}: Global size ({nx,ny}) too small to create {nsub} subdomains')
        if 0 in rankx:
            logs.abort(f'Grid {self.label}: Global x size {nx} too small to create {nsub} subdomains')
        if 0 in ranky:
            logs.abort(f'Grid {self.label}: Global y size {ny} too small to create {nsub} subdomains')
    
        # return results
        return rankx, ranky

    def make_local_subdomain(self,domid,nsub):
        """
        Decompose the global grid in subdomains. Identify the local subdomain properties. Select the Halo grid corresponding to subdomain.
        
        Parameters
        ----------
        domid : int
            subdomain index to create
        nsub : int
            number of subdomains to decompose

        Raises
        ------
            Abort if subdomain ID is negative or greater than number of subdomain
            Abort if halos size make them to overlap themselves
            
        """
        # check arguments
        self.subdom = domid
        if domid > nsub:
            logs.abort(f'Grid {self.label}: Subdomain ID {domid} is greater than Grid subdomains {nsub}')
        if domid < 0:
            logs.abort(f'Grid {self.label}: Subdomain ID {domid} should not negative')
        
        # divide grid in subdomains
        logs.info(f'        Configure grid {self.label} for subdomain {domid+1} out of {nsub+1} with {halo_size} halo cells.')
        sub_sizes_x, sub_sizes_y = self.decompose(nsub)

        # local grid dimension
        isub = domid % len(sub_sizes_x)
        jsub = domid // len(sub_sizes_x)
        self.loc_size = ( sub_sizes_x[isub] , sub_sizes_y[jsub] )
        self.global_offset = sum(sub_sizes_y[0:jsub]) * self.size[0] + sum(sub_sizes_x[0:isub])
            
        # create halos
        self.halos = HaloGrid.select_type( self.grd, self.fold, self.bnd, self.halo_size, self.size, self.loc_size, self.global_offset )
        
    def as_box_partition(self):
        """ Returns subdomain real cells (only) as parameters useable by OASIS to define a sending Box Partition. """
        return self.global_offset, self.loc_size[0], self.loc_size[1], self.size[0]
        
    def as_orange_partition(self):
        """ Returns subdomain real and halo cells as parameters useable by OASIS to define a receiving Orange Partition. """
        # segment real cells
        seg_offsets = []
        seg_sizes = []
        for l in range(self.loc_size[1]):
            start = self.global_offset + self.size[0] * l
            seg_offsets.append( start )
            seg_sizes.append( self.loc_size[0] )
        
        # segment halos cells
        halos_offsets, halos_sizes = self.halos.segment()
        
        # gather segments for oasis
        seg_offsets += halos_offsets
        seg_sizes += halos_sizes
        seg_offsets, seg_sizes = clean_for_oasis( seg_offsets , seg_sizes)
        
        # total size of orange partition
        self.orange_size = sum(seg_sizes)
        return seg_offsets, seg_sizes, self.size[0]*self.size[1]
        
    def rebuild(self,oasis_field):
        """ Rebuild a received field from OASIS into subdomain shape with real and halo cells. """
        return self.halos.rebuild(oasis_field)
        
    def format_sending_array(self,sending_array,var_label=''):
        """ Convert a real and halo cells shaped subdomain field into a sending-compatible shape. """
        # check array
        if not isinstance(sending_array, np.ndarray):
            logs.abort(f'Grid {self.label}: Sending array for {var_label} must by a numpy array')
        if len(sending_array.shape) != 3:
            logs.abort(f'Grid {self.label}: Shape of sending array for {var_label} must be equal to 3 and is {len(sending_array.shape)}')
        if ( sending_array.shape[0]*sending_array.shape[1] ) != ( self.loc_size[0]*self.loc_size[1] ):
            logs.abort(f'Grid {self.label}: Size of sending array for {var_label} does not match partition {self.loc_size[0]*self.loc_size[1]}')

        # remove halos
        hls = self.halos.size
        return sending_array[ hls : sending_array.shape[0]-hls , hls : sending_array.shape[1]-hls , : ]
                
    def generate_receiving_array(self,nlvl=1):
        """ Generate an array whose shape matches OASIS reception raw format.
        
        Parameters
        ----------
            nlvl : int
                number of third dimension level to generate, (default=1)
        
        """
        return np.zeros( (self.orange_size,nlvl) )

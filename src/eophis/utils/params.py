"""
params.py - This module contains useful constants
"""

class Freqs:
    """
    This class contains pre-defined commonly used exchange frequencies for coupled run
    
    Attributes:
        STATIC (int): dummy integer for OASIS
        HOURLY (int): 3600 seconds
        DAILY (int): 24 x HOURLY
        WEEKLY (int): 7 x DAILY
        MONTHLY (int): 31 x DAILY
        YEARLY (int): 365 x DAILY
    """
    STATIC = -1
    MINUTLY = 60
    HOURLY = 3600
    DAILY = 24 * HOURLY
    WEEKLY = 7 * DAILY
    MONTHLY = 31 * DAILY
    YEARLY = 365 * DAILY


class Grids:
    """
    This class contains pre-defined commonly used earth grids for coupled run.
    Grid is a tuple containing:
        nlon (int): number of longitude points
        nlat (int): number of latitude points
        lon_overlap (int): number of overlapping longitude points if periodic (0 otherwise)
        lat_overlap (int): number of overlapping latitude points if periodic (0 otherwise)
    
    Attributes:
        eORCA05 (tuple): (nlon = 720, nlat = 603, lon_overlap = 2, lat_overlap = 2)
        eORCA025 (tuple): (nlon = 1440, nlat = 1206, lon_overlap = 2, lat_overlap = 2)
    """
    eORCA05 = (720,603,2,2)
    eORCA025 = (1442,1207,0,0)

"""
param.py - This module contains useful constants
"""

__all__ = ['Freqs','set_mode']

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


class Mode:
    """
    This class contains the different eophis modes
    
    Attributes:
        PREPROD (bool): Preprodution mode ; enables namelists writing, disables OASIS initialization
        PROD (bool): Production mode ; disables namelist writing, enables OASIS initialization and namelist consistency checking (default mode)
    """
    PREPROD = False
    PROD = True

def set_mode(mode_to_set):
    """ Change eophis Mode to mode_to_set (str): 'preprod' or 'prod' """
    if mode_to_set == 'preprod':
        Mode.PREPROD = True
        Mode.PROD = False
    elif mode_to_set == 'prod':
        Mode.PREPROD = False
        Mode.PROD = True
    else:
        Mode.PREPROD = False
        Mode.PROD = False

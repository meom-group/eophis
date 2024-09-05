"""
This module contains useful constants.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""

__all__ = ['Freqs','set_mode']

class Freqs:
    """
    This class contains pre-defined exchange frequencies.
    
    Notes
    -----
    STATIC is equal -1 to be identified by Namcouple. It is replaced by the total
    simulation time value during writing of OASIS namelist.
    
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
    This class contains the status of eophis modes.
    
    PREPROD : bool
        Preprodution mode : enables namelists writing, disables OASIS initialization
    PROD : bool
        Production mode : disables namelist writing, enables OASIS initialization and namelist consistency checking (default mode)
        
    """
    PREPROD = False
    PROD = True


def set_mode(mode_to_set):
    """
    Changes eophis Mode.
    
    Parameters
    ----------
    mode_to_set : string
        'preprod' or 'prod'
        
    Notes
    -----
    - preprod : Preprodution mode enables namelists writing and disables OASIS initialization
    - prod : Production mode disables namelist writing and enables OASIS initialization and namelist consistency checking (default mode)
        
    """
    if mode_to_set == 'preprod':
        Mode.PREPROD = True
        Mode.PROD = False
    elif mode_to_set == 'prod':
        Mode.PREPROD = False
        Mode.PROD = True
    else:
        Mode.PREPROD = False
        Mode.PROD = False

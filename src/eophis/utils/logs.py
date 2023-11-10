"""
logs.py - This module creates and configures eophis log files
"""

# eophis modules
from .params import RANK
# external modules
import logging
import inspect

__all__ = ['info','warning','abort']

def info(message=''):
    """
    Write informational message in 'eophis.out' log file
    
    Args:
        message (str): message to be logged
    """
    _logger_info.info(message) if RANK == 0 else None

def warning(message='Warning not described'):
    """
    Write a warning message in 'eophis.err' log file
    Write that a warning occured in 'eophis.out' log file
    
    Args:
        message (str): warning message to be logged
    """
    if RANK == 0:
        caller = inspect.stack()[1]
        _logger_err.warning('from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
        _logger_info.info(f'Warning raised ! See error log for details\n')

def abort(message='Error not described'):
    """
    Write an error message in 'eophis.err' log file
    Write that a warning occured in 'eophis.out' log file
    Stop execution
    
    Args:
        message (str): error message to be logged
    """
    if RANK == 0 :
        caller = inspect.stack()[1]
        _logger_info.info('RUN ABORTED, see error log for details')
        _logger_err.error('from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
    quit()

def _setup_logger(name, log_file, formatter, level=logging.INFO):
    """
    Create a logger
    
    Args:
       name (str): logger name
       log_file (str): file name for logger outputs
       formatter (class logging.Formatter): Ouputs message format
       level (int): logger output level
    
    Returns:
        logger (logging.Logger): The logger object for writing messages
    """
    handler = logging.FileHandler(log_file,mode='w')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


_format = logging.Formatter('%(message)s')
_format_err = logging.Formatter('%(levelname)s %(message)s')

_logger_info = _setup_logger('logger_info','eophis.out',_format)
_logger_err = _setup_logger('logger_err','eophis.err',_format_err,logging.WARNING)

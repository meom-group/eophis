"""
log.py - This module creates and configures eophis log files
"""
# eophis modules
from .worker import Paral, quit_eophis
# external modules
import logging
import inspect

__all__ = ['info','warning','abort']

class Logbuffer:
    """
    This class contains the log buffer. It is used to store outputs message until the Master process is identified,
    which is not possible while coupling environement is not set.
    
    Attributes:
        content (list): list of output messages
        fill (bool): use buffer if True, nothing otherwise
    """
    content = []
    store = True

def flush_buffer(writer=Paral.RANK):
    """ Write content of log buffer in the log files """
    if Logbuffer.store:
        Logbuffer.store = False
        for message in Logbuffer.content:
            _logger_info.info(message,writer)


def info(message='',writer=Paral.MASTER):
    """
    Write informational message in 'eophis.out' log file
    
    Args:
        message (str): message to be logged
    """
    if Logbuffer.store:
        Logbuffer.content.append(message)
    else:
        _logger_info.info(message) if Paral.RANK == writer else None


def warning(message='Warning not described'):
    """
    Write a warning message in 'eophis.err' log file
    Write that a warning occured in 'eophis.out' log file
    
    Args:
        message (str): warning message to be logged
    """
    caller = inspect.stack()[1]
    _logger_err.warning('[RANK:'+str(Paral.RANK)+'] from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
    info('Warning raised by rank '+str(Paral.RANK)+' ! See error log for details\n',Paral.RANK)


def abort(message='Error not described'):
    """
    Write an error message in 'eophis.err' log file
    Write that a error occured in 'eophis.out' log file
    Stop execution
    
    Args:
        message (str): error message to be logged
    """
    caller = inspect.stack()[1]
    _logger_err.error('[RANK:'+str(Paral.RANK)+'] from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
    info('RUN ABORTED by rank '+str(Paral.RANK)+' see error log for details',Paral.RANK)
    flush_buffer()
    quit_eophis()


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
    if Paral.RANK == Paral.MASTER: 
        mode='w'
    else:
        mode='a'

    handler = logging.FileHandler(log_file,mode=mode)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
    

_format = logging.Formatter('%(message)s')
_format_err = logging.Formatter('%(levelname)s %(message)s')

_logger_info = _setup_logger('logger_info','eophis.out',_format)
_logger_err = _setup_logger('logger_err','eophis.err',_format_err,logging.WARNING)

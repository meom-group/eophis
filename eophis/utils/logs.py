"""
This module creates and configures eophis log files.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""
# eophis modules
from .worker import Paral, quit_eophis
# external modules
import logging
import inspect

__all__ = ['info','warning','abort']

class _Logbuffer:
    """
    This class contains the log buffer. It is used to store output messages until the Master process is identified,
    which is not possible while coupling environement is not set.
    
    Attributes
    ----------
    content : list( string )
        list of stored output messages
    store : bool
        store output messages in log buffer if True, does not otherwise
        
    """
    content = []
    store = True

def flush_buffer(writer=Paral.RANK):
    """ Calling process writes content of log buffer in log files """
    if _Logbuffer.store:
        _Logbuffer.store = False
        for message in _Logbuffer.content:
            info(message,writer)


def info(message='',writer=Paral.MASTER):
    """
    Write informational message in 'eophis.out' log file.
    
    Parameters
    ----------
    message : string
        message to be logged
    writer : int
        rank of process that shall write
        
    """
    if _Logbuffer.store:
        _Logbuffer.content.append(message)
    else:
        _logger_info.info(message) if Paral.RANK == writer else None


def warning(message='Warning not described'):
    """
    Write a warning message in 'eophis.err' log file.
    Write that a warning occured in 'eophis.out' log file.
    
    Parameters
    ----------
    message : string
        warning message to be logged
        
    """
    caller = inspect.stack()[1]
    _logger_err.warning('[RANK:'+str(Paral.RANK)+'] from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
    info('Warning raised by rank '+str(Paral.RANK)+' ! See error log for details\n',Paral.RANK)


def abort(message='Error not described'):
    """
    Write an error message in 'eophis.err' log file.
    Write that a error occured in 'eophis.out' log file.
    Stop execution.
    
    Parameters
    ----------
    message : string
        error message to be logged
        
    """
    caller = inspect.stack()[1]
    _logger_err.error('[RANK:'+str(Paral.RANK)+'] from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
    info('RUN ABORTED by rank '+str(Paral.RANK)+' see error log for details',Paral.RANK)
    flush_buffer()
    quit_eophis()


def _setup_logger(name, log_file, formatter, level=logging.INFO):
    """
    Create a logger
    
    Parameters
    ----------
    name : string
        logger name
    log_file : string
        file name for logger outputs
    formatter : class logging.Formatter
        Ouputs message format
    level : int
        logger output level
    
    Returns
    -------
    logger : logging.Logger
        logger object to write messages
        
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
    
# define and create formats and loggers for warning and info logs
_format = logging.Formatter('%(message)s')
_format_err = logging.Formatter('%(levelname)s %(message)s')

_logger_info = _setup_logger('logger_info','eophis.out',_format)
_logger_err = _setup_logger('logger_err','eophis.err',_format_err,logging.WARNING)

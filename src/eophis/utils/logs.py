# eophis modules
from .params import RANK
# external modules
import logging
import inspect

__all__ = ['info','warning','abort']

def info(message=''):
    _logger_info.info(message) if RANK == 0 else None

def warning(message='Warning not described'):
    if RANK == 0:
        caller = inspect.stack()[1]
        _logger_err.warning('from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
        _logger_info.info(f'Warning raised ! See error log for details\n')

def abort(message='Error not described'):
    if RANK == 0 :
        caller = inspect.stack()[1]
        _logger_info.info('RUN ABORTED, see error log for details')
        _logger_err.error('from '+caller.filename+' at line '+str(caller.lineno)+': '+message)
    quit()

def _setup_logger(name, log_file, formatter, level=logging.INFO):
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

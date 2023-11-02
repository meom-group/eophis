# eophis modules
from .params import RANK
# external modules
import logging

__all__ = ['info','warning','abort']

def info(message=''):
    _logger_info.info(message) if RANK == 0 else None

def warning(message='Warning not described'):
    _logger_err.warning(message) if RANK == 0 else None

def abort(message='Error not described'):
    if RANK == 0 :
        _logger_info.info('RUN ABORTED, see error log for details')
        _logger_err.error(message)
    quit()

def _setup_logger(name, log_file, formatter, level=logging.INFO):
    handler = logging.FileHandler(log_file,mode='w')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


_format = logging.Formatter('%(levelname)s %(message)s')
_format_err = logging.Formatter('%(levelname)s from %(module)s at line %(lineno)s: %(message)s')

_logger_info = _setup_logger('logger_info','eophis.out',_format)
_logger_err = _setup_logger('logger_err','eophis.err',_format_err,logging.WARNING)

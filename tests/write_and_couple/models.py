"""
Contains User Inference/Analytic Models or Functions.

A model must fit the following requisites and structure :
-------------------------------------------------------
    1. must be a callable function that takes N numpy arrays as inputs
    2. /!\ returns N None for the N awaited outputs if at least one of the input is None /!\
    3. inputs may be freely formatted and transformed into what you want BUT...
    4. ...outputs must be formatted as numpy array for sending back
"""
import numpy as np

#             Utils            #
# ++++++++++++++++++++++++++++ #
def Is_None(*inputs):
    """ Test presence of at least one None in inputs """
    return any(item is None for item in inputs)

# ============================ #
#          Add Hundred         #
# ============================ #
def add_100(sst):
    """ Trivially add 100 to sst (numpy.ndarray) """
    if Is_None(sst):
        return None
    else:
        return np.add(sst,200)

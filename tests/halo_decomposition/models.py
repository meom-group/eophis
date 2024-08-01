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

# ======================= #
#      Compute Delta      #
# ======================= #
def deltaxy(fld):
    """  """
    if Is_None(fld):
        return None, None
    else:
        dx = np.diff(fld,axis=0,append=fld[0:1,:,:])
        dy = np.diff(fld,axis=1,prepend=fld[:,0:1,:])
        return dx , dy

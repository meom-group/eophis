"""
Contains User Inference/Analytic Models or Functions.

A model must fit the following requisites and structure :
-------------------------------------------------------
    1. must be a callable function that takes N numpy arrays as inputs
    2. returns N None for the N awaited outputs if at least one of the input is None
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
def compute_gradient( # ... ):
    """ Compute gradient of dat (numpy.ndarray) against x (numpy.ndarray) """
    if Is_None(dat,x):
        return # ...
    else:
        # ...
        # ...
        # ...
        
        
if __name__ == '__main__':
    # Generate inputs
    shape = (50,25,10)
    dat = np.random.rand(*shape)
    x = np.random.rand(*shape)
    # Pass in model
    forcing = compute_gradient(dat,x)
    print(f'Returned forcing shape: {forcing.shape}')
    print(f'Test successful')

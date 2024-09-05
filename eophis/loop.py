"""
This module contains time loop structures to synchronize connexions between coupled scripts.

* Copyright (c) 2023 IGE-MEOM
    Eophis is released under an MIT License.
    See the `LICENSE <https://github.com/meom-group/eophis/blob/main/LICENSE>`_ file for details.
"""
# eophis modules
from .utils import logs
from .coupling import Tunnel, tunnels_ready
# external modules
import datetime

def starter(loop_router):
    """
    Starter for Loop-Router assembly.
    
    Parameters
    ----------
    assembled_loop : function
        Loop-Router to start
        
    """
    loop_router()


def all_in_all_out(geo_model,step,niter):
    """
    Builds a Loop on All In All Out (AIAO) structure. ``assembler()`` function inserts ``router()``
    inside ``base_loop()`` in which receivings and sendings steps are pre-defined.
    
    Parameters
    ----------
    geo_model : eophis.Tunnel
        coupling Tunnel to perform exchanges with earth
    step : int
        loop time step, in seconds
    niter : int
        number of loop iteration
        
    Returns
    -------
    base_loop : function
        AIAO loop completed with ``router()``
        
    Raises
    ------
    eophis.abort()
        if no router defined to construct loop
    eophis.abort()
        if loop starts with tunnels not ready
        
    Notes
    -----
    An AIAO loop orchestrates the following steps:
        1. receive all data from earth
        2. transfert data to models (provided from ``router()``)
        3. send back all results
    
    Example
    -------
    >>> @all_in_all_out(coupledEarth,timeStep,timeIter)
    >>> def router(**inputs):
    >>>     outputs = {}
    >>>     outputs[varToSendBack] = my_model(inputs[varReceived])
    >>>     return outputs
    
    """
    final_date = datetime.timedelta(seconds=niter*step)
    step_date = datetime.timedelta(seconds=step)
    
    def assembler(router=None):
        def base_loop(*args, **kwargs):
            logs.info(f'\n-------------------- RUN LOOP ----------------------')
            logs.info(f'Number of iterations : {niter}')
            logs.info(f'Time step : {step}s -- {step_date}')
            logs.info(f'Total Time : {niter*step}s -- {final_date} \n')

            # check router
            if callable(router):
                logs.info('Router: ...TO BE COMPLETED...\n')
            else:
                logs.abort('No Router defined for coupled run')

            # check static variables status
            if not tunnels_ready():
                logs.abort('Static variables must be exchanged before starting any loop')

            for it in range(niter):
                it_sec = int(step * it)
                date = datetime.timedelta(seconds=it_sec)
                date_info = f'Iteration {it+1}: {it_sec}s -- {date} \n'
                
                # perform all receptions
                # ----------------------
                arrays = { varin : geo_model.receive(varin,it_sec) for varin in geo_model.arriving_list() }
                if not all( type(arr) == type(None) for arr in arrays.values() ):
                    requests = ", ".join( [ varin for varin,arr in arrays.items() if type(arr) is not type(None) ] )
                    logs.info(f'{date_info}   Treating {requests} received through tunnel {geo_model.label}')
                    
                # Modeling
                # --------
                inferences = router(**arrays)

                # perform all sendings
                # --------------------
                [ geo_model.send(varout,inf,it_sec) for varout,inf in inferences.items() ]
                if not all( type(arr) == type(None) for arr in arrays.values()  ):
                    results = ", ".join( [ varout for varout,inf in inferences.items() if type(inf) is not type(None) ] )
                    logs.info(f'   Sending back {results} through tunnel {geo_model.label}')

            logs.info(f'------------------- END OF LOOP -------------------')
        return base_loop
    return assembler

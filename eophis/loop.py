"""
This module contains time loop structures to synchronize connexions between coupled Earth-System and Inferences Models.
"""
# eophis modules
from .utils import logs
from .coupling import Tunnel, tunnels_ready
# external modules
import datetime

def starter(assembled_loop):
    """
    Starter for constructed loops.
    
    Parameters
    ----------
    assembled_loop : function
        loop to start
        
    """
    assembled_loop()


def all_in_all_out(earth_system,step,niter):
    """
    Build a custom time loop on All In All Out (AIAO) structure. ``assembler()`` function inserts ``modeling_routine()``
    inside ``base_loop()`` in which receivings and sendings steps are pre-defined.
    
    Parameters
    ----------
    earth_system : eophis.Tunnel
        coupling Tunnel to perform exchanges with earth
    step : int
        loop time step, in seconds
    niter : int
        number of loop iteration
        
    Returns
    -------
    base_loop : function
        AIAO loop completed with ``modeling_routine()``
        
    Raises
    ------
    eophis.abort()
        if no modeling routine defined to construct loop
    eophis.abort()
        if loop starts with tunnels not ready
        
    Notes
    -----
    An AIAO loop orchestrates the following steps:
        1. receive all data from earth
        2. transfert data to models (provided from ``modeling_routine()``)
        3. send back all results
    
    Example
    -------
    >>> @all_in_all_out(coupledEarth,timeStep,timeIter)
    >>> def transfert_instructions(**inputs):
    >>>     outputs = {}
    >>>     outputs[varToSendBack] = my_model(inputs[varReceived])
    >>>     return outputs
    
        
    """
    final_date = datetime.timedelta(seconds=niter*step)
    step_date = datetime.timedelta(seconds=step)
    
    def assembler(modeling_routine=None):
        def base_loop(*args, **kwargs):
            logs.info(f'\n-------------------- RUN LOOP ----------------------')
            logs.info(f'Number of iterations : {niter}')
            logs.info(f'Time step : {step}s -- {step_date}')
            logs.info(f'Total Time : {niter*step}s -- {final_date} \n')

            # check modeling routine
            if callable(modeling_routine):
                logs.info('Modeling routine: ...TO BE COMPLETED...\n')
            else:
                logs.abort('No modeling routine defined for coupled run')

            # check static variables status
            if not tunnels_ready():
                logs.abort('Static variables must be exchanged before starting any loop')

            for it in range(niter):
                it_sec = int(step * it)
                date = datetime.timedelta(seconds=it_sec)
                date_info = f'Iteration {it+1}: {it_sec}s -- {date} \n'
                
                # perform all receptions
                # ----------------------
                arrays = { varin : earth_system.receive(varin,it_sec) for varin in earth_system.arriving_list() }
                if not all( type(arr) == type(None) for arr in arrays.values() ):
                    requests = ", ".join( [ varin for varin,arr in arrays.items() if type(arr) is not type(None) ] )
                    logs.info(f'{date_info}   Treating {requests} received through tunnel {earth_system.label}')
                    
                # Modeling
                # --------
                inferences = modeling_routine(**arrays)

                # perform all sendings
                # --------------------
                [ earth_system.send(varout,inf,it_sec) for varout,inf in inferences.items() ]
                if not all( type(arr) == type(None) for arr in arrays.values()  ):
                    results = ", ".join( [ varout for varout,inf in inferences.items() if type(inf) is not type(None) ] )
                    logs.info(f'   Sending back {results} through tunnel {earth_system.label}')

            logs.info(f'------------------- END OF LOOP -------------------')
        return base_loop
    return assembler

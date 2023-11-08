# eophis modules
from .utils import logs
from .coupling import Tunnel
# external modules
import datetime

# wrapper to run built loop
def start(assembled_loop):
    assembled_loop()

# All In All Out : receive everything - modeling routine - send everything
def all_in_all_out(earth_system,step,niter):

    final_date = datetime.timedelta(seconds=niter*step)
    step_date = datetime.timedelta(seconds=step)
    
    def assembler(modeling_routine=None):
        def base_loop(*args, **kwargs):
            logs.info(f'\n-------------------- RUN LOOP ----------------------')
            logs.info(f'Number of iterations : {niter}')
            logs.info(f'Time step : {step}s -- {step_date}')
            logs.info(f'Total Time : {niter*step}s -- {final_date} \n')

            if callable(modeling_routine):
                logs.info('Modeling routine: ...TO BE COMPLETED...\n')
            else:
                logs.abort('No modeling routine defined for coupled run')

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
                [ earth_system.send(varout,it_sec,inf) for varout,inf in inferences.items() ]
                if not all( type(arr) == type(None) for arr in arrays.values()  ):
                    results = ", ".join( [ varout for varout,inf in inferences.items() if type(inf) is not type(None) ] )
                    logs.info(f'   Sending back {results} through tunnel {earth_system.label}')

            logs.info(f'------------------ END OF LOOP -------------------------')
        return base_loop
    return assembler

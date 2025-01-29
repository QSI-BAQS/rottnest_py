from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.widget_compilers.compiler_flow import run_widget as run_widget
import multiprocessing as mp
import traceback
import time

def pool_worker_main(task_queue: mp.Queue, worker_results_queue: mp.Queue):
    '''
    execute_compute_unit should not throw
    '''
    print("Worker started", flush=True)
    while True:
        args = task_queue.get()
        if args == 'ping':
            worker_results_queue.put('pong')
            continue
        execute_compute_unit(args, worker_results_queue)

def execute_compute_unit(args, worker_results_queue: mp.Queue):
    # print("got", args, flush=True)
    import sys
    # old_stdout = sys.stdout # Enable printing
    f = open('/dev/null', 'w')
    sys.stdout = f
    old_stdout = sys.stdout # Disable printing

    print("running elem", flush=True)
    try:
        compute_unit, rz_tag_tracker, full_output, cache_hash = args
        compute_unit: ComputeUnit

        stats = {
            'cu_id': compute_unit.unit_id,
            'status': 'running',
            'cache_hash': cache_hash,
        }

        arch_json_obj = compute_unit.get_architecture_json()

        # worker_results_queue.put(stats.copy())

        widget = compute_unit.compile_graph_state()

        print("compile done", flush=True, file=old_stdout)

        # Debug output widget outputs
        # with open('debug_obj.json', 'w') as f:
        #     print(widget.json(), file=f)

        orch = run_widget(cabaliser_obj=widget.json(), region_obj=arch_json_obj, full_output=full_output, rz_tag_tracker=rz_tag_tracker)
        
        print("execution done", flush=True, file=old_stdout)
        
        stats = {
            'volumes': orch.get_space_time_volume(),
            't_source': orch.get_T_stats(),
            'tocks': orch.get_total_cycles(),
            'vis_obj': None,
            'cu_id': compute_unit.unit_id,
            'status': 'complete',
            'cache_hash': cache_hash,
        }

        print(stats)

        if full_output:
            stats['vis_obj'] = orch.json
        
        print("storing result", flush=True, file=old_stdout)

        worker_results_queue.put(stats)

    except Exception as e:
        tb = traceback.format_exception(e)

        # Debug output exceptions
        # with open('errors.out', 'a') as f:
        #     print('=============file===========', file=f)
        #     print(widget.json(), file=f)
        #     print('=============tb===========', file=f)
        #     print(''.join(tb), file=f)

        stats = {
            'cu_id': str(compute_unit.unit_id), 
            'err_type': repr(e), 
            'traceback': tb,
            'status': 'error',
        }

        worker_results_queue.put(stats)
    finally:
        sys.stdout = old_stdout

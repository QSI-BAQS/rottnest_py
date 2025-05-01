from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.widget_compilers.compiler_flow import run_widget as run_widget
import multiprocessing as mp
import traceback
import time

def pool_worker_main(task_queue: mp.Queue, worker_results_queue: mp.Queue, is_priority: bool = False):
    '''
    execute_compute_unit should not throw
    '''
    print("Worker started:", mp.current_process().name, flush=True)
    while True:
        task, *args = task_queue.get()
        if task == 'ping':
            print("Worker received ping")
            worker_results_queue.put('pong')
            continue
        elif task == 'exc_cu':
            execute_compute_unit(args, worker_results_queue, is_priority)
        elif task == 'get_graph':
            from rottnest.server.model.graph_view import get_graph
            try:
                worker_results_queue.put(get_graph(args[0]))
            except:
                import traceback
                traceback.print_exc()
                worker_results_queue.put('ERROR')
        elif task == 'exc_graph_node':
            try:
                execute_graph_node(args[0], args[1], worker_results_queue)
            except:
                import traceback
                traceback.print_exc()
                worker_results_queue.put('ERROR')

def execute_graph_node(node_hash, arch_obj, worker_results_queue: mp.Queue):
    from rottnest.server.model.graph_view import view_cache
    from rottnest.compute_units.sequencer import Sequencer
    from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker
    from rottnest.compute_units.architecture_proxy import saved_architectures
    from rottnest.input_parsers import pyliqtr_parser
    
    saved_architectures[-666666] = arch_obj
    node = view_cache[node_hash]
    parser = node.parser
    print(parser)
    pyliqtr_parser.local_cache = set()
    seq = Sequencer(-666666)

    it = seq.sequence_pyliqtr(parser)

    # Yields (compute_unit, rz_tag_tracker, full_output)
    wrapped_it = ((obj, shared_rz_tag_tracker, True, None, None) for obj in it)

    # Should only be one compute unit per obj
    # Iterator here is for sanity checking  
    for args in wrapped_it:
        print(args)
        execute_compute_unit(args, worker_results_queue, True)

    worker_results_queue.put('end')


def execute_compute_unit(args, worker_results_queue: mp.Queue, is_priority):
    # print("got", args, flush=True)

    if not is_priority:
        import sys
        # old_stdout = sys.stdout # Enable printing
        f = open('/dev/null', 'w')
        sys.stdout = f
        old_stdout = sys.stdout # Disable printing
    else:
        import sys
        old_stdout = sys.stdout

    print("running elem", flush=True)
    try:
        compute_unit, rz_tag_tracker, full_output, cache_hash, np_qubits = args
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
        if is_priority:
            with open('debug_obj.json', 'w') as f:
                print(widget.json(), file=f)

        orch = run_widget(cabaliser_obj=widget.json(), region_obj=arch_json_obj, full_output=full_output, rz_tag_tracker=rz_tag_tracker)
        
        print("execution done", flush=True, file=old_stdout)
        
        stats = {
            'volumes': orch.get_space_time_volume(),
            't_source': orch.get_T_stats(),
            'tocks': orch.get_tock_stats(),
            'vis_obj': None,
            'cu_id': compute_unit.unit_id,
            'status': 'complete',
            'cache_hash': cache_hash,
            'np_qubits': np_qubits,
        }

        stats['tocks']['total'] = sum(stats['tocks'].values())
        
        print(stats)

        if full_output:
            stats['vis_obj'] = orch.json
        
        print("storing result", flush=True, file=old_stdout)

        worker_results_queue.put(stats)

    except Exception as e:
        tb = traceback.format_exception(e)
        try:
            # Debug output exceptions
            with open('errors.out', 'a') as f:
                print('=============file===========', file=f)
                print(widget.json(), file=f)
                print('=============tb===========', file=f)
                print(''.join(tb), file=f)
        except:
            pass

        try:
            stats = {
                'cu_id': str(getattr(compute_unit, "unit_id", "ERROR")), 
                'err_type': repr(e), 
                'traceback': tb,
                'status': 'error',
                'cache_hash': cache_hash,
                'np_qubits': np_qubits,
            }
        except:
            stats = {
                'cu_id': "MISSING",
                'status': 'fatal',
            }

        worker_results_queue.put(stats)
    finally:
        sys.stdout = old_stdout

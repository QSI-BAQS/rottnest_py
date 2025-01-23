import multiprocessing as mp
from threading import Thread
from typing import Any
from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.widget_compilers.main import run as run_widget
import time 

N_PROCESSES = 8

# result_manager = mp.Manager()
# dummy_result_cache = result_manager.dict()

class Debug:
    def __init__(self, obj = None):
        self.obj = obj
    unit_id = 'debug'
    def compile_graph_state(self):
        return self
    
    def json(self):
        if self.obj is None:
            return {
                "n_qubits": 4,
                "consumptionschedule": [[{0: []}], [{1: [0]}], [{2: [1]}], [{3: [2]}]],
                "adjacencies": {0: [1], 1: [0], 2: [3], 3: [2]}
            }
        else:
            import json
            return json.load(self.obj)


def run_sequence_elem(args):
    import sys
    f = open('/dev/null', 'w')
    sys.stdout = f
    print("running elem", flush=True)
    compute_unit, arch_obj, full_output = args
    compute_unit: ComputeUnit
    # TODO replace with actual impl + add try/except
    try:
        # TODO signal running here
        stats = {
            'cu_id': compute_unit.unit_id,
            'status': 'running'
        }
        widget = compute_unit.compile_graph_state()
        print("compile done", flush=True)
        # Debug output widget outputs
        # with open('debug_obj.json', 'w') as f:
        #     print(widget.json(), file=f)
        orch = run_widget(cabaliser_obj=widget.json(), region_obj=arch_obj, full_output=full_output)
        print("execution done", flush=True)
        
        stats = {
            'volumes': orch.get_space_time_volume(),
            't_source': orch.get_T_stats(),
            'vis_obj': None,
            'cu_id': compute_unit.unit_id,
            'status': 'complete'
        }
        print(stats)
        if full_output:
            stats['vis_obj'] = orch.json
        print("returning result")
        return (False, stats)
    except Exception as e:
        import traceback
        tb = traceback.format_exception(e)
        # Debug output exceptions
        # with open('errors.out', 'a') as f:
        #     print('=============file===========', file=f)
        #     print(widget.json(), file=f)
        #     print('=============tb===========', file=f)
        #     print(''.join(tb), file=f)
        return (True, {'cu_id': str(compute_unit.unit_id), 'err_type': repr(e), 'traceback': tb})

def task_run_sequence(arch_obj):
    from rottnest.executables.current_executable import current_executable
    parser = PyliqtrParser(current_executable)
    parser.parse()
    seq = Sequencer(arch_obj)


    # Actual work here.
    it = seq.sequence_pyliqtr(parser)
    task_work_fn = run_sequence_elem
    task_args_additional = (arch_obj, False)

    print("circuit done")
    return (it, task_work_fn, task_args_additional)

operation_map = {"task_run_sequence": task_run_sequence}


class AsyncIteratorProcessPool:    
    @staticmethod
    def _manager_main(task_queue: mp.Queue, completion_queue: mp.Queue, completion_callback: Any):
        print("in manager main")
        pool = mp.Pool(N_PROCESSES)

        while True:
            task_name, *args = task_queue.get()

            print("got task", task_name)

            if task_name == 'terminate':
                break
            
            it, work_fn, work_args = operation_map[task_name](*args)

            wrapped_iter = ((obj, *work_args) for obj in it)

            def wrapped_iter_test(it):
                for i, obj in enumerate(it):
                    if i > 0:
                        break
                    yield (obj, *work_args)
            print("start time:", time.time())
            n_completed = 0
            for (is_err, payload) in pool.imap_unordered(work_fn, wrapped_iter):
                n_completed += 1
                print("completed count", n_completed, "@", time.time())
                # s = str(payload)
                # if not is_err: # Always print full errors
                #     s = s[:min(200, len(s))]

                #     print("pool completed", s)
                # else:
                #     print("pool completed err:")
                #     print(''.join(payload['traceback']))
                # result_cache[payload['cu_id']] = payload
                # completion_callback(payload, err=is_err)
            print("iterator exhausted!")
            print("time:", time.time())

        pool.terminate()

    def __init__(self, completion_callback):
        self.task_queue = mp.Queue()
        self.manager = Thread(target=self._manager_main, args=[self.task_queue, None, completion_callback],
                              name="PoolManager")
        self.manager.start()
        print("init done")
        # TODO delete, we don't need this field
        self.completion_callback = completion_callback

    def pool_submit(self, task_name, *args):
        if task_name == "debug":
            test_obj = Debug('debug_obj2.json')
            # test_obj = next(iter(task_run_sequence(args[0])[0]))
            print("args:", args)
            (is_err, payload) = run_sequence_elem((test_obj, args[0], False))
            if not is_err: # Always print full errors
                s = str(payload)
                s = s[:min(200, len(s))]
                print("pool completed", s)
            else:
                print("pool completed err:")
                print(''.join(payload['traceback']))

            # dummy_result_cache[payload['cu_id']] = payload
            # self.completion_callback(payload, err=is_err)
            return
        # return
        self.task_queue.put((task_name, *args))

    def terminate(self):
        self.task_queue.put(('terminate', ))
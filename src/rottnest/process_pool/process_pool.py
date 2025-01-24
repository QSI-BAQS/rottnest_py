import multiprocessing as mp
from threading import Thread
from typing import Any
from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
import time 
import queue

from rottnest.process_pool.process_worker import pool_worker_main
from rottnest.executables.current_executable import current_executable

N_PROCESSES = 8
SEGFAULT_SENTINEL_TIMEOUT_SECS = 20
# result_manager = mp.Manager()
# dummy_result_cache = result_manager.dict()

class DebugComputeUnit:
    unit_id = 'debug'
    
    def __init__(self, obj = None):
        self.obj = obj
    
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

class ComputeUnitExecutorPool:
    @staticmethod
    def _pool_manager_entrypoint(manager_task_queue: mp.Queue, 
                                 manager_completion_queue: mp.Queue):
        '''
            Entrypoint for pool manager
        '''

        print("in manager main")

        ctx = mp.get_context('spawn')
        mp_manager = ctx.Manager()

        worker_task_queue = mp_manager.Queue(maxsize=4 * N_PROCESSES)
        worker_result_queue = mp_manager.Queue()

        pool = [
            ctx.Process(target=pool_worker_main, 
                        name="PoolWorker", 
                        args=(worker_task_queue, worker_result_queue), 
                        daemon=True)
            for _ in range(N_PROCESSES)
        ]

        for proc in pool:
            proc.start()

        while True:
            task_name, *args = manager_task_queue.get()

            print("manager got task", task_name)

            if task_name == 'terminate':
                break
            elif task_name == 'run_sequence':
                arch_obj = args[0]
                it = ComputeUnitExecutorPool._run_sequence(arch_obj)
            elif task_name == 'ping':
                # Wait for at least one worker to start
                worker_task_queue.put('ping')
                assert worker_result_queue.get() == 'pong'
                manager_completion_queue.put('pong')
                continue


            def wrapped_iter_test(it, limit):
                for i, obj in enumerate(it):
                    if i > limit:
                        break
                    yield obj

            # it = wrapped_iter_test(it, 50)

            # it = iter(it)

            print("manager job start time:", time.time())

            n_submitted = 0
            n_received = 0
            n_error = 0

            for obj in it:
                if worker_task_queue.full():
                    while not worker_result_queue.empty():
                        result = worker_result_queue.get()
                        print("received", n_received)
                        manager_completion_queue.put(result)
                        n_received += 1
                    
                    # Check status of processes
                    restart = []
                    for i, proc in enumerate(pool):
                        if proc.exitcode is not None:
                            n_error += 1
                            print(f"proc {i} exited with {proc.exitcode}, err count = {n_error}")
                            proc.join()
                            restart.append(i)
                    for i in restart:
                        print(f"restarting worker {i}")
                        pool[i] = ctx.Process(target=pool_worker_main, 
                                    name="PoolWorker", 
                                    args=(worker_task_queue, worker_result_queue), 
                                    daemon=True)
                        pool[i].start()
    
                print("submitting", n_submitted)
                worker_task_queue.put(obj)
                print("submitted", n_submitted)
                n_submitted += 1
                
            
            print("all submitted!")

            try:
                while n_received < n_submitted:
                    result = worker_result_queue.get(timeout=SEGFAULT_SENTINEL_TIMEOUT_SECS)
                    print("received", n_received)
                    manager_completion_queue.put(result)
                    n_received += 1            
            except queue.Empty:
                print(f"aborting, sentinel secs reached at {n_received}/{n_submitted} received ({n_error} errors)")
                print(f"unaccounted items: {n_submitted - n_received - n_error}")
            print("all received")
            print("time:", time.time())

        pool.terminate()

    @staticmethod
    def _run_sequence(arch_obj):
        parser = PyliqtrParser(current_executable)
        parser.parse()

        seq = Sequencer(arch_obj)

        it = seq.sequence_pyliqtr(parser)
        task_args_additional = (arch_obj, False)

        wrapped_it = ((obj, *task_args_additional) for obj in it)

        print("iterator generation done")

        return wrapped_it

    def __init__(self):
        ctx = mp.get_context('spawn')
        self.manager_task_queue = ctx.Queue()
        self.manager_completion_queue = ctx.Queue()
        self.manager = ctx.Process(target=self._pool_manager_entrypoint, 
                                   args=[self.manager_task_queue, self.manager_completion_queue],
                                   name="PoolManager")
        self.manager.start()
    
    def run_sequence(self, arch_obj):
        self.manager_task_queue.put(('run_sequence', arch_obj))
    
    def terminate(self):
        self.task_queue.put(('terminate', ))
    
    def ping(self):
        '''
        Startup delay wait
        '''
        self.manager_task_queue.put(('ping',))
        assert self.manager_completion_queue.get() == 'pong'
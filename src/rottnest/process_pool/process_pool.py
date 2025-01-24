import multiprocessing as mp
from threading import Thread
from typing import Any
from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
import time 
import queue
import select

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
                                 manager_completion_queue: mp.Queue,
                                 manager_priority_task_queue: mp.Queue,
                                 manager_priority_completion_queue: mp.Queue):
        '''
            Entrypoint for pool manager
        '''

        print("in manager main")

        ctx = mp.get_context('spawn')

        worker_task_queue = ctx.Queue(maxsize=4 * N_PROCESSES)
        worker_result_queue = ctx.Queue()

        pool = [
            ctx.Process(target=pool_worker_main, 
                        name="PoolWorker", 
                        args=(worker_task_queue, worker_result_queue), 
                        daemon=True)
            for _ in range(N_PROCESSES)
        ]
        #############################
        # Priority data structures + setup
        #############################
        priority_task_queue = ctx.Queue()
        priority_result_queue = ctx.Queue()

        priority_submitted_count = 0
        priority_received_count = 0
        priority_error_count = 0

        priority_process = ctx.Process(target=pool_worker_main, 
                                       name="PoolWorker(Priority)", 
                                       args=(priority_task_queue, priority_result_queue), 
                                       daemon=True)
        priority_process.start()
        
        def check_restart_priority_worker():
            nonlocal priority_error_count, priority_process

            if priority_process.exitcode is not None:
                # Process died
                priority_error_count += 1
                priority_process.join()
                priority_process = ctx.Process(target=pool_worker_main, 
                                    name="PoolWorker(Priority)", 
                                    args=(priority_task_queue, priority_result_queue), 
                                    daemon=True)
                priority_process.start()

        # Probably not best to do a nested function here
        def check_run_priority():
            nonlocal priority_submitted_count, priority_process
            nonlocal manager_priority_task_queue

            while not manager_priority_task_queue.empty():
                # Get task
                obj = manager_priority_task_queue.get() # This should not block, now that we checked
                print("manager got priority task", obj)
                # Check if process is alive
                check_restart_priority_worker()

                # Submit task
                priority_task_queue.put(obj)
                print("submitted priority", priority_submitted_count)
                priority_submitted_count += 1

        def check_priority_result():
            nonlocal priority_received_count, priority_process
            nonlocal manager_priority_completion_queue

            # Check if process is alive
            check_restart_priority_worker()

            while priority_error_count + priority_received_count < priority_submitted_count:
                try:
                    result = priority_result_queue.get_nowait()
                    print("received priority", priority_received_count)
                    priority_received_count += 1

                    manager_priority_completion_queue.put(result)
                except queue.Empty:
                    break

        for proc in pool:
            proc.start()

        #############################
        # Main loop
        #############################

        manager_task_fds = [manager_task_queue._reader, manager_priority_task_queue._reader]
        while True:
            # Wait until either task queue is ready for reading
            select.select(manager_task_fds, [], [])

            # Trigger priority task check
            check_run_priority()
            check_priority_result()

            # Keep waiting if no task is sent
            if manager_task_queue.empty(): 
                continue

            task_name, *args = manager_task_queue.get() # This should not block -- we checked earlier

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

            # Submit all jobs provided by sequencer
            # This loop blocks when task queue is full
            for obj in it:
                # Trigger priority task check
                check_run_priority()
                check_priority_result()

                if worker_task_queue.full():
                    while not worker_result_queue.empty():
                        result = worker_result_queue.get() # This should not block, now that we checked
                        print("received", n_received)
                        manager_completion_queue.put(result)
                        n_received += 1
                    
                    # Check status of processes and restart dead processes
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

                while True:
                    # Spin until either we get a priority task or we are unblocked on the worker task

                    check_run_priority()
                    check_priority_result()

                    if not worker_task_queue.full():
                        worker_task_queue.put(obj) # This may block, so check
                        break
                    else:
                        time.sleep(0.1) # Wait for space in worker task queue

                print("submitted", n_submitted)
                n_submitted += 1
                
            
            print("all submitted!")

            # Read remaining data from processes
            # This loops and blocks up to SEGFAULT_SENTINEL_TIMEOUT_SECS
            # Note that priority tasks are not processed if this blocks
            try:
                while n_received < n_submitted:
                    # Trigger priority task check
                    check_run_priority()
                    check_priority_result()

                    result = worker_result_queue.get(timeout=SEGFAULT_SENTINEL_TIMEOUT_SECS)
                    print("received", n_received)
                    manager_completion_queue.put(result)
                    n_received += 1

            except queue.Empty:
                print(f"aborting, sentinel secs reached at {n_received}/{n_submitted} received ({n_error} errors)")
                print(f"unaccounted items: {n_submitted - n_received - n_error}")

            print("all received")
            print("time:", time.time())

        # Cleanup after receiving "terminate"
        for proc in pool:
            proc.terminate()
        
        priority_process.terminate()

        for proc in pool:
            proc.join()

        priority_process.join()

    @staticmethod
    def _run_sequence(arch_obj):
        parser = PyliqtrParser(current_executable)
        parser.parse()

        seq = Sequencer(arch_obj)

        it = seq.sequence_pyliqtr(parser)

        # Yields (compute_unit, architecture_json_obj, full_output)
        wrapped_it = ((obj, arch_obj, False) for obj in it)

        print("iterator generation done")

        return wrapped_it

    def __init__(self):
        ctx = mp.get_context('spawn')
        self.manager_task_queue = ctx.Queue()
        self.manager_completion_queue = ctx.Queue()
        self.manager_priority_task_queue = ctx.Queue()
        self.manager_priority_completion_queue = ctx.Queue()

        self.manager = ctx.Process(target=self._pool_manager_entrypoint, 
                                   args=[self.manager_task_queue, 
                                         self.manager_completion_queue,
                                         self.manager_priority_task_queue,
                                         self.manager_priority_completion_queue],
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
    
    def run_priority(self, compute_unit, arch_obj, full_output=True):
        self.manager_priority_task_queue.put((compute_unit, arch_obj, full_output))
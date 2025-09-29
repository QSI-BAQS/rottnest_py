from enum import Enum, auto
import multiprocessing as mp
from threading import Thread
from typing import Any
from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
import rottnest.input_parsers.pyliqtr_parser as pyliqtr_parser
import time 
import queue
import select
from copy import deepcopy

from collections import defaultdict, deque

from rottnest.process_pool.process_worker import pool_worker_main
from rottnest.executables.current_executable import current_executable

from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker
from rottnest.compute_units.architecture_proxy import saved_architectures

#from rottnest.pandora import pandora_cache 

# TODO: Move these to an appropriate config
N_PROCESSES = 64 * 2 
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

def _add_dict(d1, d2):
    return {
        k: d1.get(k, 0) + d2.get(k, 0)
        for k in d1.keys() | d2.keys()
    }

def add_result_dicts(res1, res2):
    return {
        'volumes': _add_dict(res1.get('volumes', {}), res2.get('volumes', {})),
        't_source': _add_dict(res1.get('t_source', {}), res2.get('t_source', {})),
        'tocks': _add_dict(res1.get('tocks', {}), res2.get('tocks', {})),
    }

def _iadd_dict(d1, d2):
    for k in d2:
        d1[k] = d1.get(k, 0) + d2[k]

def iadd_result_dicts(res1, res2):
    if 'volumes' not in res1:
        res1['volumes'] = {}
    if 't_source' not in res1:
        res1['t_source'] = {}
    if 'tocks' not in res1:
        res1['tocks'] = {}
    _iadd_dict(res1['volumes'], res2.get('volumes', {}))
    _iadd_dict(res1['t_source'], res2.get('t_source', {}))
    _iadd_dict(res1['tocks'], res2.get('tocks', {}))

class ComputeUnitExecutorPoolManager:
    def __init__(self, 
                 manager_task_queue: mp.Queue, 
                 manager_completion_queue: mp.Queue,
                 manager_priority_task_queue: mp.Queue,
                 manager_priority_completion_queue: mp.Queue):

        self.manager_task_queue = manager_task_queue
        self.manager_completion_queue = manager_completion_queue
        self.manager_priority_task_queue = manager_priority_task_queue
        self.manager_priority_completion_queue = manager_priority_completion_queue

        self.ctx = mp.get_context('spawn')

        self.worker_task_queue = self.ctx.Queue(maxsize=4 * N_PROCESSES)
        self.worker_result_queue = self.ctx.Queue()

        self.pool = [
            self.ctx.Process(target=pool_worker_main, 
                        name=f"PoolWorker{i}", 
                        args=(self.worker_task_queue, self.worker_result_queue), 
                        daemon=True)
            for i in range(N_PROCESSES)
        ]

        #############################
        # Priority data structures + setup
        #############################
        self.priority_task_queue = self.ctx.Queue()
        self.priority_result_queue = self.ctx.Queue()

        self.priority_submitted_count = 0
        self.priority_received_count = 0
        self.priority_error_count = 0

        self.priority_process = self.ctx.Process(target=pool_worker_main, 
                                       name="PoolWorker(Priority)", 
                                       args=(self.priority_task_queue, self.priority_result_queue, True), 
                                       daemon=True)
        self.priority_process.start()

        for proc in self.pool:
            proc.start()

        self.manager_task_fds = [self.manager_task_queue._reader, 
                                 self.manager_priority_task_queue._reader, 
                                 self.priority_result_queue._reader]

        self.compute_unit_result_cache = defaultdict(dict)

    @staticmethod
    def entrypoint(*args, **kwargs):
        manager = ComputeUnitExecutorPoolManager(*args, **kwargs)
        manager.main_loop()

    def main_loop(self):
        
        while True:
            # Wait until either (1) normal task, (2) priority task, or 
            # (3) priority result is available
            select.select(self.manager_task_fds, [], [])

            # Do priority override here
            self.check_run_priority()
            self.check_priority_result()

            # Task available: run task
            if not self.manager_task_queue.empty():
                if self.run_task(): break

    def send_total(self, cu_id="TOTAL"):
        totals = self.compute_unit_result_cache[None]
        totals['cu_id'] = cu_id
        self.manager_completion_queue.put(totals)
        print("TOTAL: ", totals)
        print("ERRORS: ", self.n_error)
    
    def run_task(self):
        '''
        Returns true if exiting, none otherwise
        '''
        # This should not block -- we checked before calling this
        task_name, *args = self.manager_task_queue.get() 
        if task_name == 'terminate':
            return True
        elif task_name == 'ping':
            # Wait for at least one worker to start
            # print("manager got ping")
            self.worker_task_queue.put(('ping',))
            # print("waiting for child pong")
            assert self.worker_result_queue.get() == 'pong'
            self.manager_completion_queue.put('pong')
            return
        
        if task_name != 'run_sequence':
            raise Exception(f"Unknown task: {task_name}")
        
        self.run_seq_start = time.time()
        print("manager job start time:", self.run_seq_start)

        self.n_submitted = 0
        self.n_received = 0
        self.n_error = 0

        self.compute_unit_counts = defaultdict(int)
        self.compute_unit_totals = defaultdict(int)
        self.cache_hash_stack = [None]
        self.np_stack = [0]
        if None in self.compute_unit_result_cache:
            del self.compute_unit_result_cache[None]

        self.sequencer_time = 0
        self.cache_time = 0

        # Submit all jobs provided by sequencer
        # This loop blocks when task queue is full

        arch_ids = args[0]
        it = ComputeUnitExecutorPool._run_sequence(arch_ids)

        def wrapped_iter_test(it, limit):
            for i, obj in enumerate(it):
                if i > limit:
                    break
                yield obj

        # it = wrapped_iter_test(it, 0)

        update_counter = 20

        for obj in it:
        # while True:
        #     seq_start = time.time()
        #     obj = next(it, StopIteration)
        #     self.sequencer_time += (time.time() - seq_start)
        #     if obj == StopIteration:
        #         break

            if obj[0] == INTERRUPT:
                self.process_elem_cache(obj)
            else:
                self.process_elem_obj(obj)

            update_counter -= 1
            if update_counter < 0:
                update_counter = 20
                self.send_total()
        
        print("all submitted!")
        print("last non-cache job at", self.submit_time, "delta", self.submit_time - self.run_seq_start)
        print("sequencer time:", self.sequencer_time, "cache_time:", self.cache_time)

        # Read remaining data from processes
        # This loops and blocks up to SEGFAULT_SENTINEL_TIMEOUT_SECS
        # Note that priority tasks are not processed if this blocks
        try:
            while self.n_received < self.n_submitted:
                # Trigger priority task check
                self.check_run_priority()
                self.check_priority_result()

                self.process_result_elem(timeout=SEGFAULT_SENTINEL_TIMEOUT_SECS)

        except queue.Empty:
            print(f"aborting, sentinel secs reached at {self.n_received}/{self.n_submitted} received ({self.n_error} errors)")
            print(f"unaccounted items: {self.n_submitted - self.n_received - self.n_error}")

        self.send_total()
        self.send_total("endcomp")
        #print(compute_unit_totals)
        self.manager_completion_queue.put('done')

        print("all received")
        print("time:", time.time() - self.run_seq_start)

    def process_result_elem(self, timeout=None):
        '''
        Blocking read from worker_result_queue and process result
        '''
        result = self.worker_result_queue.get(timeout=timeout)
        if result.get('status', 'error') == 'error': # Probably an error, dump to stdout
            print(result)

        result_hash_stack = result.get('cache_hash', [None])
        np_stack = result.get('np_qubits', [0])
        tock_dict = result.get('tocks', {})
        np_dur = tock_dict.get('bell', 0) + tock_dict.get('t_schedule', 0) + tock_dict.get('bell2', 0)
        if 'volumes' not in result:
            result['volumes'] = {}

        old_volume = result['volumes'].get('NP_VOLUME', 0) 
        result['volumes']['NP_VOLUME'] = old_volume

        # print(result_hash_stack, np_stack)

        for i, stack_hash in enumerate(reversed(result_hash_stack)):
            self.compute_unit_counts[stack_hash] += 1
            iadd_result_dicts(
                self.compute_unit_result_cache[stack_hash], result
            )
            result['volumes']['NP_VOLUME'] += np_stack[-i-1] * np_dur

        result['volumes']['NP_VOLUME'] = old_volume

        # print(compute_unit_counts, compute_unit_totals)

        print("received", self.n_received)
        self.manager_completion_queue.put(result)
        self.n_received += 1

    def process_elem_cache(self, obj):
        cache_start = time.time()
        cache_obj = obj[0]
        check={CACHED.START: "START", CACHED.END: "END", CACHED.REQUEST: "REQ"}
        # print(cache_obj.cache_hash(), check[cache_obj.request_type])

        # Process cache command
        if cache_obj.request_type == CACHED.START:
            self.cache_hash_stack.append(cache_obj.cache_hash())
            self.np_stack.append(cache_obj.non_participatory_qubits)

        elif cache_obj.request_type == CACHED.END:
            if self.cache_hash_stack[-1] != cache_obj.cache_hash():
                raise Exception("Received unmatched cache_end in stream", cache_obj.cache_hash(), self.cache_hash_stack)
            
            cache_hash = self.cache_hash_stack.pop()
            non_participatory = self.np_stack.pop()

        elif cache_obj.request_type == CACHED.REQUEST:
            # Process result from cache
            cache_hash = cache_obj.cache_hash()
            while not self.process_cache_request(cache_hash, np_qubits = cache_obj.non_participatory_qubits):
                # Barrier until we can resolve this cache request
                self.process_result_elem()

        self.cache_time += time.time() - cache_start

    def process_elem_obj(self, obj):
        self.submit_time = time.time()

        for stack_hash in self.cache_hash_stack:
            self.compute_unit_totals[stack_hash] += 1

        if self.worker_task_queue.full() or self.worker_result_queue.qsize() > 50:
            while not self.worker_result_queue.empty():
                # Drain result queue
                self.process_result_elem()
            
            # Check status of processes and restart dead processes
            restart = []
            for i, proc in enumerate(self.pool):
                if proc.exitcode is not None:
                    n_error += 1
                    print(f"proc {i} exited with {proc.exitcode}, err count = {n_error}")
                    proc.join()
                    restart.append(i)
            for i in restart:
                print(f"restarting worker {i}")
                self.pool[i] = self.ctx.Process(target=pool_worker_main, 
                            name=f"PoolWorker{i}", 
                            args=(self.worker_task_queue, self.worker_result_queue), 
                            daemon=True)
                self.pool[i].start()

        print("submitting", self.n_submitted)

        while True:
            # Spin until either we get a priority task or we are unblocked on the worker task

            self.check_run_priority()
            self.check_priority_result()

            if not self.worker_task_queue.full():
                self.worker_task_queue.put(('exc_cu', *obj, self.cache_hash_stack.copy(), self.np_stack.copy())) # This may block, so check
                break
            else:
                time.sleep(0.1) # Wait for space in worker task queue
        
        print("submitted", self.n_submitted)
        self.n_submitted += 1

    def process_cache_request(self, cache_hash, np_qubits = 0) -> bool:
        '''
        Returns true if success, false if blocking on previously submitted compute units
        '''
        if self.compute_unit_counts[cache_hash] != self.compute_unit_totals[cache_hash]:
            return False
        
        output = deepcopy(self.compute_unit_result_cache[cache_hash])
        output['cache_hash_hex'] = cache_hash.hex()
        # print("output:", output, self.compute_unit_counts, self.compute_unit_totals)
        self.manager_completion_queue.put(output)

        tock_dict = output.get('tocks', {})
        np_dur = tock_dict.get('bell', 0) + tock_dict.get('t_schedule', 0) + tock_dict.get('bell2', 0)
        if 'volumes' not in output:
            output['volumes'] = {}

        old_volume = output['volumes'].get('NP_VOLUME', 0) 
        output['volumes']['NP_VOLUME'] = old_volume + np_qubits * np_dur

        for i,stack_hash in enumerate(reversed(self.cache_hash_stack)):
            iadd_result_dicts(
                self.compute_unit_result_cache[stack_hash], output
            )
            output['volumes']['NP_VOLUME'] += self.np_stack[-i-1] * np_dur

        output['volumes']['NP_VOLUME'] = old_volume

        # print(sum(self.np_stack, start=np_qubits), self.compute_unit_result_cache[None]['volumes']['NP_VOLUME'], self.compute_unit_result_cache[None]['tocks']['total'])

        return True

    def check_restart_priority_worker(self):
        if self.priority_process.exitcode is not None:
            # Process died
            self.priority_error_count += 1
            self.priority_process.join()
            self.priority_process = self.ctx.Process(target=pool_worker_main, 
                                name="PoolWorker(Priority)", 
                                args=(self.priority_task_queue, self.priority_result_queue), 
                                daemon=True)
            self.priority_process.start()

    def check_run_priority(self):
        global saved_architectures

        while not self.manager_priority_task_queue.empty():
            # Get task
            task, args = self.manager_priority_task_queue.get() # This should not block, now that we checked

            if task == "run_priority":
                print("manager got priority task", task, args)
                # Check if process is alive
                self.check_restart_priority_worker()

                # Submit task
                self.priority_task_queue.put(args)
                print("submitted priority", self.priority_submitted_count)
                self.priority_submitted_count += 1
            elif task == "save_arch":
                arch_id, arch_json_obj = args
                saved_architectures[arch_id] = arch_json_obj
    
    def check_priority_result(self):
        # Check if process is alive
        self.check_restart_priority_worker()

        while self.priority_error_count + self.priority_received_count < self.priority_submitted_count or not self.priority_result_queue.empty():
            try:
                result = self.priority_result_queue.get_nowait()
                print("received priority", self.priority_received_count)
                self.priority_received_count += 1

                self.manager_priority_completion_queue.put(result)
            except queue.Empty:
                break

class ComputeUnitExecutorPool:    
    @staticmethod
    def _run_sequence(arch_ids):

        # Drops cache if the architecture changes
        if pyliqtr_parser.local_cache_tag != arch_ids:
            pyliqtr_parser.local_cache_tag = arch_ids
            pyliqtr_parser.local_cache = set()


        # TODO: De-hard code this at some point
        global saved_architectures

        # Set the pandora union find based on the architecture
        #pandora_cache.architecture_bind(arch_ids[0])

        parser = PyliqtrParser(current_executable())
        parser.parse()
        
        seq = Sequencer(*arch_ids)

        it = seq.sequence_pyliqtr(parser)

        # Yields (compute_unit, rz_tag_tracker, full_output)
        wrapped_it = ((obj, shared_rz_tag_tracker, False) for obj in it)

        print("iterator generation done")

        return wrapped_it

    def __init__(self):
        self.ctx = mp.get_context('spawn')
        self.manager_task_queue = self.ctx.Queue()
        self.manager_completion_queue = self.ctx.Queue()
        self.manager_priority_task_queue = self.ctx.Queue()
        self.manager_priority_completion_queue = self.ctx.Queue()

    def start(self):
        self.manager = self.ctx.Process(target=ComputeUnitExecutorPoolManager.entrypoint, 
                                   args=[self.manager_task_queue, 
                                         self.manager_completion_queue,
                                         self.manager_priority_task_queue,
                                         self.manager_priority_completion_queue],
                                   name="PoolManager")
        self.manager.start()
    
    def run_sequence(self, arch_ids):
        self.manager_task_queue.put(('run_sequence', arch_ids))
    
    def terminate(self):
        self.task_queue.put(('terminate', ))
    
    def ping(self):
        '''
        Startup delay wait
        '''
        self.manager_task_queue.put(('ping',))
        assert self.manager_completion_queue.get() == 'pong'
    
    def run_priority(self, compute_unit, rz_tag_tracker, full_output=True):
        self.manager_priority_task_queue.put(("run_priority", ('exc_cu', compute_unit, rz_tag_tracker, full_output, [None], 0)))

    
    def run_priority_graph_node(self, node_name, arch_obj):
        self.manager_priority_task_queue.put(("run_priority", ('exc_graph_node', node_name, arch_obj)))

    def save_arch(self, arch_id, arch_json_obj):
        self.manager_priority_task_queue.put(("save_arch", (arch_id, arch_json_obj)))

    def get_graph(self, graph_id):
        self.manager_priority_task_queue.put(("run_priority", ('get_graph', graph_id)))

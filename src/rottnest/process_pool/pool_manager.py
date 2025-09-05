import time
import multiprocessing as mp

import typing
import select
from collections import defaultdict, deque

from rottnest.input_parsers.interrupt import INTERRUPT, CACHED
from rottnest.config import REPORT_INTERVAL, RESULT_INTERVAL
from rottnest.architecture_interface import rottnest_worker

from rottnest.rz_decomposer.rz_decomposer import DEFAULT_PRECISION

from rottnest.compute_units.compilation_producers import generate_compute_units

from .symbols import TOTAL, SPAWN_CONTEXT, PONG 

from rottnest.process_pool import commands, symbols

from rottnest.config import N_PROCESSES, SEGFAULT_SENTINEL_TIMEOUT_SECS

from rottnest.compute_units.layout_proxy import LayoutProxy

class ComputeUnitExecutorPoolManager:
    '''
        Manages communications with process pool workers
    '''

    def __init__(self, 
                 manager_task_queue: mp.Queue, 
                 manager_completion_queue: mp.Queue,
                 manager_priority_task_queue: mp.Queue,
                 manager_priority_completion_queue: mp.Queue,
                 *,
                 worker = None):
        '''
            Manager class for the process pool
        '''
        # Internal import to for instantiation
        from rottnest.plugins import architectures, executables 
        self._architectures = architectures
        self._executables = executables

        self.composer = None
        self._rz_precision = DEFAULT_PRECISION 

        # Cache management
        # TODO: Move this into the composer 
        self.non_participatory_stack = [0]
        self.cache_hash_stack = [None]
        self.compute_unit_result_cache = defaultdict(dict)
        
        # Manager Communication queues 
        self.manager_task_queue = manager_task_queue
        self.manager_completion_queue = manager_completion_queue

        # Dedicated priority task queue
        self.manager_priority_task_queue = manager_priority_task_queue
        self.manager_priority_completion_queue = manager_priority_completion_queue

        self.ctx = mp.get_context(symbols.SPAWN_CONTEXT)

        # Worker queues
        # TODO: add network queue
        self.worker_task_queue = self.ctx.Queue(
            maxsize = 4 * N_PROCESSES
        )
        self.worker_result_queue = self.ctx.Queue()
    
        # Entrypoints
        self._architecture = None 
        self.pool = list()
        self.priority_process = None

        self.manager_running = True
        self.pool_running = False 

        #############################
        # Priority data structures + setup
        #############################
        self.priority_task_queue = self.ctx.Queue()
        self.priority_result_queue = self.ctx.Queue()

        self.priority_submitted_count = 0
        self.priority_received_count = 0
        self.priority_error_count = 0

        # Default precision
        self.precision_bits = 10
        
        # File desciptors
        self.manager_task_fds = [
            self.manager_task_queue._reader, 
            self.manager_priority_task_queue._reader, 
            self.priority_result_queue._reader
        ]

        # Task selector
        self._tasks = {
            commands.PING: self._task_ping,
            commands.PING_MANAGER: self._task_ping_manager,
            commands.START_WORKERS: self._task_start_workers,
            commands.STOP_WORKERS: self._task_stop_workers,
            commands.TERMINATE: self._task_terminate,
            commands.RUN_SEQUENCE: self._task_run_sequence,
            commands.SYNCHRONISE_MODULES: self._task_synchronise_modules,
            commands.SYNCHRONISE_LAYOUTS: self._task_synchronise_layouts,

            commands.SET_ARCHITECTURE_MODULE: self._task_set_architecture_module,
            commands.SET_EXECUTABLE: self._task_set_executable,
            commands.SET_EXECUTABLE_PARAMS: self._task_set_executable_params,
            commands.SET_PRECISION: self._task_set_precision
        }

    @staticmethod
    def entrypoint(*args, **kwargs):
        '''
            Entrypoint function for the manager
        '''
        manager = ComputeUnitExecutorPoolManager(*args, **kwargs)
        print("Started Manager")
        manager.main_loop()

    def main_loop(self):
        '''
            Main loop for manager 
            Sits and waits for either: 
            - A task
            - A priority task
            - A priority result
        '''        
        while self.manager_running:
            select.select(
                self.manager_task_fds,
                [],
                []
            )

            # TODO: Do priority override here
            #self.check_run_priority()
            #self.check_priority_result()

            # Task available: run task
            if not self.manager_task_queue.empty():
                self.run_task()
        return

    def _task_synchronise_layouts(self, *args):
        '''
            Loads a layout to the manager
            Only uses the with_id constructor to ensure
            synchronisation of ids across processes
        '''
        for layout_id, layout_json in args[0]: 
            LayoutProxy.add_layout_with_id(
                layout_id, layout_json
            )

    def initialise_composer(self, layouts, executable):
        arch = self._architectures.get_current_architecture()
        self.composer = arch.composer(layouts, list(executable.get_qubits()))

    def _task_start_workers(self, *args):
        '''
            Starts the pool
            This is decoupled from initialisation to allow 
             for worker swapping 
        '''
        if self.pool_running:
            # Workers already running, return
            return
        
        arch = self._architectures.get_current_architecture()
        worker_entrypoint = arch.worker_entrypoint

        layouts = list(LayoutProxy.get_layouts())

        print("Starting Pool")
        self.pool_running = True

        print("Layout: ", layouts)
        self.priority_process = self.ctx.Process(
            target=arch.worker.entrypoint, 
            name="PoolWorker(Priority)", 
            args=(
                self.priority_task_queue,
                self.priority_result_queue,
                layouts,
                self._rz_precision
                ), 
            daemon=True
        )

        self.pool = [
            self.ctx.Process(target=arch.worker.entrypoint, 
                        name=f"PoolWorker{i}", 
                        args=(
                            self.worker_task_queue, 
                            self.worker_result_queue,
                            layouts
                        ),
                        daemon=True)
            for i in range(N_PROCESSES)
        ]
        
        self.priority_process.start()
        for proc in self.pool:
            proc.start()

        self.pool_running = True
        print("Pool Started")
   
    def run_task(self):
        '''
            Task selector entrypoint
            Takes a task from the manager task queue
            Distributes the task to the workers 
            Then reports any results back to the manager
             completion queue.
        '''
        task_name, *args = self.manager_task_queue.get()
        task = self._tasks.get(task_name, None)
        if task is None: 
            raise Exception(f"Unknown task: {task_name}")
        else:
            result = task(*args)
            # If a response occurs, pass it back
            if result is not None:
                self.manager_completion_queue.put(result)

    def _task_terminate(self, *args):
        '''
            Terminate the pool
        '''
        self.manager_running = False
        self.pool_running = False 
        # TODO, incorporate worker shutdown
        return None

    def _task_ping_manager(self, *args):
        '''
            Checks that the manager is alive 
        '''
        # This should not block 
        return PONG 

    def _task_ping(self, *args):
        '''
            Checks that at least one worker is alive
        '''
        # Requires that the pool is running
        assert self.pool_running

        # This should not block 
        self.worker_task_queue.put((commands.PING,))
        assert self.worker_result_queue.get() == PONG 
        return PONG 

    def _task_synchronise_modules(self, *args):
        '''
            Synchronises loaded modules
        '''
        print("Synching: ", args)
        architectures = args[0]
        executables = args[1]
        self._architectures.load_modules_from_strings(*architectures) 
        self._executables.load_modules_from_strings(*executables) 

    def _task_set_architecture_module(self, *args):
        '''
            Sets an architecture module from a key
        '''
        key = args[0] 
        self._architectures.set_current_architecture(key)

    def _task_set_executable(self, *args):
        '''
            Sets an executable from a key
        '''
        key = args[0] 
        self._executables.set_current_executable(key)

    def _task_set_precision(self, *args):
        '''
            Sets the precision of the manager
        '''
        self._precision = args[0]

    def _task_set_executable(self, *args):
        '''
            Sets an executable from a key
        '''
        precision_bits = args[0] 
        self.precision_bits = precision_bits

    def _task_set_executable_params(self, *args):
        params = args[0]
        self._executables.set_executable_params(**params)

    def distribute_compilation(self, it: typing.Iterator, composer: "RottnestComposer"):
        '''
            Consumes the iterator and distributes 
            compilation among the workers 
        '''

        update_counter = REPORT_INTERVAL 

        # Consume the iterator 
        for obj in it:
            # Interupts trigger cache updates
            if obj == INTERRUPT:
                self.process_elem_cache(obj, composer)
            else:
                # Non interrupts trigger compilation 
                self.process_elem_obj(obj, composer)

            # Update reports after each interval
            update_counter -= 1
            if update_counter < 0:
                self.post_result_queue()
                update_counter = REPORT_INTERVAL
                self.send_total()

    def in_place_compilation(it: typing.Iterator):
        '''
            Consumes the iterator while performing compilation on a single core
        '''
        arch = architecture.get_current_architecture()  

        # Sets up a singular worker
        worker = arch.worker() 

        for arch_id, architecture in saved_architectures.items():
            worker.load_architecture(arch_id, architecture)

        # Consume the iterator 
        for obj in it:
            # Interupts trigger cache updates
            if obj[0] == INTERRUPT:
                self.process_elem_cache(obj)
            else:
                # Non interrupts trigger compilation 
                results = worker.exec_compute_unit(*obj)
                # TODO: combine results
        return


    def _task_run_sequence(self, *args):
        '''
            Returns true if exiting, none otherwise
        '''
        self.run_seq_start = time.time()
        print("Manager job start time:", self.run_seq_start)

        self.n_submitted = 0
        self.n_received = 0
        self.n_error = 0

        self.compute_unit_counts = defaultdict(int)
        self.compute_unit_totals = defaultdict(int)
        
        if None in self.compute_unit_result_cache:
            del self.compute_unit_result_cache[None]

        self.sequencer_time = 0
        self.cache_time = 0

        # Submit all jobs provided by sequencer
        # This loop blocks when task queue is full

        arch_ids = args[0]

        architecture = self._architectures.get_current_architecture() 
        executable = self._executables.get_current_executable() 

        # Pass layouts to composer
        layouts = list(LayoutProxy.get_layouts())
        self.initialise_composer(layouts, executable)

        composer = architecture.composer(layouts, executable.get_qubits())

        it = generate_compute_units(arch_ids, architecture, executable)

        # Consume the iterator to distribute jobs to workers
        self.distribute_compilation(it, composer)        
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

                self.process_result_elem(
                    timeout=SEGFAULT_SENTINEL_TIMEOUT_SECS
                )

        except:
            print(f"Aborting, sentinel secs reached at {self.n_received}/{self.n_submitted} received ({self.n_error} errors)")
            print(f"Unaccounted items: {self.n_submitted - self.n_received - self.n_error}")

        # Send totals
        self.send_total()
        self.send_total(symbols.END_COMPUTATION)

        print("Totals:")

        print(self.compute_unit_result_cache)

        # print(compute_unit_counts, compute_unit_totals, compute_unit_result_cache)

        self.manager_completion_queue.put(symbols.DONE)

        print("All Received")
        print("time:", time.time() - self.run_seq_start)


    def process_result_elem(self, timeout=None):
        '''
        Blocking read from worker_result_queue and 
            process result
        '''
        unit_id, result = self.worker_result_queue.get(
            timeout=timeout
        )

        if result.get('status', 'error') == 'error':
            print(result)
            return

        # Composer takes result to reportable 
        composer.receive(
            unit_id,
            result
        )

        self.manager_completion_queue.put(result)
        self.n_received += 1

        return
        # Probably an error, dump to stdout
        if result.get('status', 'error') == 'error':
            print(result)

        result_hash_stack = result.get('cache_hash', [None])
        np_stack = result.get('np_qubits', [0])

        ### TO COMPOSER
        tock_dict = result.get('tocks', {})
        np_dur = tock_dict.get('bell', 0) + tock_dict.get('t_schedule', 0) + tock_dict.get('bell2', 0)
        if 'volumes' not in result:
            result['volumes'] = {}
        
        old_volume = result['volumes'].get('NP_VOLUME', 0) 
        result['volumes']['NP_VOLUME'] = old_volume

        ###

        for i, stack_hash in enumerate(
                    reversed(
                        result_hash_stack
                    )
                ):
            self.compute_unit_counts[stack_hash] += 1
            iadd_result_dicts(
                self.compute_unit_result_cache[stack_hash],
                result
            )

            # COMPOSER
            result['volumes']['NP_VOLUME'] += (
                np_stack[-i-1] * np_dur
            )

        result['volumes']['NP_VOLUME'] = old_volume

        # TODO More interesting cursors for printing
        print("Received", self.n_received)
        self.manager_completion_queue.put(result)
        self.n_received += 1


    def send_total(self, cu_id=TOTAL):
        '''
            Asynch sending of totals
        '''
        print("Sending Total!")
        totals = self.compute_unit_result_cache[None]
        totals['cu_id'] = cu_id
        self.manager_completion_queue.put(totals)


    def process_elem_cache(
        self,
        cache_obj,
        composer
    ):
        '''
            Cache message
        '''
        cache_start = time.time()

        # Process cache command
        if cache_obj.request_type == CACHED.START:
            composer.cache_entry_start(cache_obj)

        elif cache_obj.request_type == CACHED.END:
            composer.cache_entry_end(cache_obj)

        elif cache_obj.request_type == CACHED.REQUEST:
            # Process result from cache
            cache_hash = cache_obj.cache_hash()
            while not composer.cache_request(
                cache_obj
            ):
                # Barrier until we can resolve this 
                # cache request
                self.process_result_elem()

        self.cache_time += time.time() - cache_start

    def _task_stop_workers(self):
        if not self.pool_running:       
            # Pool isn't running, skip
            return

        for proc in self.pool:
            proc.terminate()
            proc.wait()

        self.pool_running = False

    def restart_dead_processes(self):
        '''
             Check status of processes and restart 
             dead processes
        '''
        restart = []
        for i, proc in enumerate(self.pool):
            if proc.exitcode is not None:
                self.n_error += 1
                print(f"proc {i} exited with {proc.exitcode}, err count = {n_error}")
                proc.join()
                restart.append(i)

        if len(restart) == 0:
            # Nothing to restart
            return

        arch = self._architectures.get_current_architecture()
        worker_entrypoint = arch.worker.entrypoint

        for i in restart:
            print(f"Restarting worker {i}")
            self.pool[i] = self.ctx.Process(
                target=worker_entrypoint, 
                name=f"PoolWorker{i}", 
                args=(
                    self.worker_task_queue,
                    self.worker_result_queue
                ), 
                daemon=True
            )
            self.pool[i].start()

    def post_result_queue(self):
        '''
        Drain the result queue and post
        '''
        while not self.worker_result_queue.empty():
            print("RECEIVED RESULT")
            # Drain result queue
            self.process_result_elem()

    def process_elem_obj(
        self,
        obj: "ComputeUnit",
        composer: "RottnestComposer"
    ):
        '''
            Triggers compilation of a compute unit
        '''
        self.submit_time = time.time()

        # TODO: Figure out what this is up to
        for stack_hash in self.cache_hash_stack:
            self.compute_unit_totals[stack_hash] += 1
        
        # Check if we need to post results 
        if (
            self.worker_task_queue.full() 
            or 
            self.worker_result_queue.qsize() 
                > RESULT_INTERVAL
            ):
            self.post_result_queue()
        
        # Restart dead processes and tally errors
        # TODO
        #self.restart_dead_processes()
            
        #print("Submitting", self.n_submitted)

        submitted = False
        while not submitted:
            # Spin until either we get a priority task or we are unblocked on the worker task

            self.check_run_priority()
            self.check_priority_result()

            # This may block, so check
            if not self.worker_task_queue.full():

                # Inform the composer
                composer.submit(compute_unit)

                # Send job to worker
                self.worker_task_queue.put(
                    (
                        rottnest_worker.EXEC_COMPUTE_UNIT,
                        obj,
                    )
                ) 
                submitted = True
            else:
                # Wait for space in queue
                time.sleep(0.1) 
        
        print("Submitted", self.n_submitted)
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

import time
import multiprocessing as mp

import queue
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

from copy import deepcopy

from .pool_status import PoolStatus
from .status_decorator import status_update, StatusTracked


class ComputeUnitExecutorPoolManager(StatusTracked):
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

        # Only really used once running
        self._status = PoolStatus.UNSTARTED

        self.composer = None
        self._rz_precision = DEFAULT_PRECISION

        # Cache management
        # TODO: Move this into the composer
        self.non_participatory_stack = [0]
        self.cache_hash_stack = [None]

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
            commands.POLL: self._task_poll,
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
            commands.SET_PRECISION: self._task_set_precision,

            commands.GET_CURRENT_RESULTS: self._task_get_results,
        }

    @staticmethod
    def entrypoint(*args, **kwargs):
        '''
            Entrypoint function for the manager
        '''
        manager = ComputeUnitExecutorPoolManager(*args, **kwargs)
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
            if not self.manager_priority_task_queue.empty():
                self.run_priority_task()

            # Task available: run task
            if not self.manager_task_queue.empty():
                self.run_task()
        return

    def get_status(self):
        '''
            Status Getter
        '''
        return self._status

    def set_status(self, status):
        '''
            Status Setter
        '''
        self._status = status

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
        self.composer.reset_result()

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

        self.pool_running = True

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

    def run_task(self, task_queue=None, completion_queue=None):
        '''
            Task selector entrypoint
            Takes a task from the manager task queue
            Distributes the task to the workers
            Then reports any results back to the manager
             completion queue.
        '''
        if task_queue is None:
            task_queue = self.manager_task_queue

        if completion_queue is None:
            completion_queue = self.manager_completion_queue

        task_name, *args = task_queue.get()
        print("Running: ", task_name, args)
        task = self._tasks.get(task_name, None)
        if task is None:
            raise Exception(f"Unknown task: {task_name}")
        else:
            print(task, args)
            result = task(*args)
            # If a response occurs, pass it back
            if result is not None:
                completion_queue.put(result)

    def run_priority_task(self):
        '''
            Run a priority task
        '''
        return self.run_task(
            task_queue = self.manager_priority_task_queue,
            completion_queue = self.manager_priority_completion_queue
        )


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

    def _task_poll(self, *args):
        '''
           Gets manager status
        '''
        # This should not block
        return self.get_status()

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

    def _task_set_executable_params(self, *args):
        params = args[0]
        self._executables.set_executable_params(**params)

    def distribute_compilation(self, it: typing.Iterator):
        '''
            Consumes the iterator and distributes
            compilation among the workers
        '''

        update_counter = REPORT_INTERVAL

        # Consume the iterator
        for obj in it:
            # Interupts trigger cache updates
            if obj == INTERRUPT:
                self.process_elem_cache(obj)
            else:
                # Non interrupts trigger compilation
                self.process_elem_obj(obj)

            # Update reports after each interval
            update_counter -= 1
            if update_counter < 0:
                self.post_result_queue()
                update_counter = REPORT_INTERVAL
                self.send_total()

    def in_place_compilation(self, it: typing.Iterator):
        '''
            Consumes the iterator while performing compilation on a single core
        '''
        arch = plugin_architecture.get_current_architecture()

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

    @status_update(
        PoolStatus.EXECUTING,
        PoolStatus.FINISHED
    )
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

        it = generate_compute_units(arch_ids, architecture, executable)

        # Consume the iterator to distribute jobs to workers
        self.distribute_compilation(it)

        # Sets composer state
        self.composer.all_submitted()
        print("all submitted!")
        print("last non-cache job at", self.submit_time, "delta", self.submit_time - self.run_seq_start)
        print("sequencer time:", self.sequencer_time, "cache_time:", self.cache_time)

        # Read remaining data from processes
        # This loops and blocks up to SEGFAULT_SENTINEL_TIMEOUT_SECS
        # Note that priority tasks are not processed if this blocks
        try:
            while not self.composer.cache_resolved or self.n_received < self.n_submitted:
                # Trigger priority task check
                self.check_run_priority()
                self.check_priority_result()

                self.process_result_elem(
                    timeout=SEGFAULT_SENTINEL_TIMEOUT_SECS
                )

        except Exception as e:
            print(e)
            print(f"Aborting, sentinel secs reached at {self.n_received}/{self.n_submitted} received ({self.n_error} errors)")
            print(f"Unaccounted items: {self.n_submitted - self.n_received - self.n_error}")

        # Send totals
        self.send_total()
        self.send_total(symbols.END_COMPUTATION)

        print("Totals:")



        self.manager_completion_queue.put(symbols.DONE)

        print("All Received")
        print("time:", time.time() - self.run_seq_start)


    def process_result_elem(self, timeout=None):
        '''
        Blocking read from worker_result_queue and
            process result
        '''
        print("Processing result")
        #obj = self.worker_result_queue.get(
        #    timeout=timeout
        #)

        unit_id, result = self.worker_result_queue.get(
            timeout=timeout
        )
        print('Result:', unit_id, str(result), type(result))

        result_obj = self.composer.compose_result(unit_id, result)

        # Composer takes result to reportable
        self.composer.receive(
            result_obj
        )

        self.manager_completion_queue.put(result_obj)

        # TODO: Batch
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
            add_result_dicts(
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
        print("Stack Frame: ", self.composer.stack_frames[0].result.to_args())
        #totals = self.compute_unit_result_cache[None]
        #totals['cu_id'] = cu_id
        #self.manager_completion_queue.put(totals)

    def _task_get_results(self, *args, **kwargs):
        '''
            Sends the results
            Wrapper around send total
        '''
        print("Getting Results")
        self.send_total()


    def process_elem_cache(
        self,
        cache_obj
    ):
        '''
            Cache message
        '''
        cache_start = time.time()

        # Process cache command
        if cache_obj.request_type == CACHED.START:
            self.composer.cache_entry_start(cache_obj)

        elif cache_obj.request_type == CACHED.END:
            self.composer.cache_entry_end(cache_obj)

        elif cache_obj.request_type == CACHED.REQUEST:
            # Process result from cache
            self.composer.cache_request(cache_obj)

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
                print(f"proc {i} exited with {proc.exitcode}, err count = {self.n_error}")
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
            # Drain result queue
            self.process_result_elem()

    def process_elem_obj(
        self,
        obj: "ComputeUnit",
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


        submitted = False
        while not submitted:
            # Spin until either we get a priority task or we are unblocked on the worker task

            self.check_run_priority()

            # This may block, so check
            if not self.worker_task_queue.full():

                # Inform the composer
                self.composer.submit(obj)

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

        self.n_submitted += 1

    def process_cache_request(self, cache_hash, np_qubits = 0) -> bool:
        '''
        Returns true if success, false if blocking on previously submitted compute units
        MOVED TO COMPOSER
        '''
        if self.compute_unit_counts[cache_hash] != self.compute_unit_totals[cache_hash]:
            return False

        output = deepcopy(self.compute_unit_result_cache[cache_hash])
        output['cache_hash_hex'] = cache_hash.hex()
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

        return True

    def check_restart_priority_worker(self):

        arch = self._architectures.get_current_architecture()
        worker_entrypoint = arch.worker_entrypoint

        if self.priority_process.exitcode is not None:
            # Process died
            self.priority_error_count += 1
            self.priority_process.join()
            self.priority_process = self.ctx.Process(target=worker_entrypoint,
                                name="PoolWorker(Priority)",
                                args=(self.priority_task_queue, self.priority_result_queue),
                                daemon=True)
            self.priority_process.start()


    def check_run_priority(self):
        '''
            Convenience function
        '''
        if not self.manager_priority_task_queue.empty():
            self.run_priority_task()


    #def check_run_priority(self):
    #    global saved_architectures

    #    while not self.manager_priority_task_queue.empty():
    #        # Get task
    #        task, args = self.manager_priority_task_queue.get() # This should not block, now that we checked

    #        if task == "run_priority":
    #            print("Manager got priority task", task, args)
    #            # Check if process is alive
    #            self.check_restart_priority_worker()

    #            # Submit task
    #            self.priority_task_queue.put(args)
    #            print("submitted priority", self.priority_submitted_count)
    #            self.priority_submitted_count += 1
    #        elif task == "save_arch":
    #            arch_id, arch_json_obj = args
    #            saved_architectures[arch_id] = arch_json_obj

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

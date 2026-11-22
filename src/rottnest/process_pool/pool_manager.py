from rottnest.priority_process.commands import GET_VISUALISER_NEXT
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
from rottnest.rz_decomposer import set_rz_precision, get_rz_precision

from rottnest.compute_units.compilation_producers import generate_compute_units

from .symbols import TOTAL, SPAWN_CONTEXT, PONG

from rottnest.process_pool import commands, symbols

from rottnest.config import N_PROCESSES, SEGFAULT_SENTINEL_TIMEOUT_SECS

from rottnest.compute_units.layout_proxy import LayoutProxy

from copy import deepcopy

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

from rottnest.priority_process import commands as priority_commands

from .pool_status import PoolStatus
from .single_instantiation import SingleInstantiation
from .status_decorator import status_update, StatusTracked
from .ipc_manager import IPCManager

# Used to hook the patching procedure
from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure

from rottnest.procedures.option_setters import procedure_load_modules, procedure_set_option
# LoadModulesProcedure, SetArchitectureProcedure, SetExecutableProcedure


from .tasks import get_pool_manager_tasks

class ComputeUnitExecutorPoolManager(StatusTracked, SingleInstantiation):
    '''
        Manages communications with process pool workers
    '''
    instantiate = True
    blocked = False  

    TIMEOUT = 5

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
        print("Manager Started")
        self.manager_running = True
        self.pool_running = False

        # Internal import for instantiation
        from rottnest.plugins import architectures, executables

        self._architectures = architectures
        self._executables = executables

        # Only really used once running
        self._status = PoolStatus.UNSTARTED

        self.composer = None
        # WARN: We need to address this conflict of names


        # Manager Communication queues
        self.manager_task_queue = manager_task_queue
        self.manager_completion_queue = manager_completion_queue

        # Dedicated priority task queue
        self.manager_priority_task_queue = manager_priority_task_queue
        self.manager_priority_completion_queue = manager_priority_completion_queue

        self.ctx = mp.get_context(symbols.SPAWN_CONTEXT)

        # Worker queues
        # TODO: add network queue
        self.worker_task_queue = None
        # For per-worker comms
        self.worker_comms_queue = None
        self.worker_result_queue = None

        # IPC manager
        self.worker_ipc = None 

        # Entrypoints
        self.pool = list()


        #############################
        # Priority data structures + setup
        #############################
        self.priority_task_queue = self.ctx.Queue()
        self.priority_result_queue = self.ctx.Queue()
        self.priority_comms_queue = self.ctx.Queue()

        self.priority_submitted_count = 0
        self.priority_received_count = 0
        self.priority_error_count = 0

        self.priority_process = self.ctx.Process(
            target=rottnest_worker.RottnestWorker.entrypoint,
            name="PoolWorker(Priority) [INITIAL]",
            args=(
                self.priority_task_queue,
                self.priority_result_queue,
                self.priority_comms_queue,
                [],
                get_rz_precision(),
                True # Priority
                ),
            daemon=True
        )
        self.priority_process.start()

        # File desciptors
        self.manager_task_fds = [
            self.manager_task_queue._reader,
            self.manager_priority_task_queue._reader,
            self.priority_result_queue._reader
        ]

        # Task selector
        #self._tasks = {
        #    priority_commands.SYNCHRONISE_PRIORITY: self._task_priority_setup,
        #    priority_commands.GET_CALLGRAPH: self._task_get_callgraph,
        #    priority_commands.GET_VISUALISER: self._task_get_visualiser,
        #    priority_commands.GET_VISUALISER_NEXT: self._task_get_visualiser_next,
        #}  
        self._tasks = get_pool_manager_tasks()

    def __del__(self, *args, **kwargs):
        '''
            Safe process shutdown
        '''
        self.stop_workers()
        self.stop_priority_worker()

    @staticmethod
    def entrypoint(*args, **kwargs):
        '''
            Entrypoint function for the manager
        '''
        manager = ComputeUnitExecutorPoolManager(*args, **kwargs)
        manager.main_loop()

    # @with_debug_log()
    def main_loop(self):
        '''
            Main loop for manager
            Sits and waits for either:
            - A task
            - A priority task
            - A priority result
        '''
        while self.manager_running:
            _result = select.select(
                self.manager_task_fds,
                [],
                [],
                self.TIMEOUT
            )
            # TODO: Do priority override here
            if not self.manager_priority_task_queue.empty():
                self.run_priority_task()

            # Task available: run task
            if not self.manager_task_queue.empty():
                self.run_task()

            # Check the priority result queues
            self.check_priority_result()

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

    def _submit(
            self,
            queue: "Queue",
            command: str,
            *args,
            **kwargs
        ):
        '''
            Submits to a queue
        '''        
        queue.put(
            (
                command,
                args,
                kwargs,
            ),
        )

    def submit_priority(
        self,
        priority_command: str,
        *args,
         **kwargs
    ):
        '''
            Submits to the priority task queue 
        '''
        self._submit(
            self.priority_task_queue,
            priority_command, *args, **kwargs
        )
    
    def broadcast_workers(
        self,
        command,
        *args,
        submit_priority_worker = True,
        **kwargs
    ):
        '''
            Broadcasts to all workers comms queues
            If `submit_priority_worker` is also set
             then also submits to the priority worker
        '''
        for queue in self.worker_comms_queue:
            self._submit(
                queue, 
                command, *args, **kwargs
            )

        if submit_priority_worker:
            # And send to priority    
            self._submit( 
                self.priority_comms_queue,
                command, *args, **kwargs
            )

    def submit_worker_task(
        self,
        command,
        *args,
        **kwargs
    ):
        '''
            Submits to the joint worker task queue
        '''
        self._submit( 
            self.worker_task_queue,
            command, *args, **kwargs
        )

    def get_postprocessing_data(self, *args):
        '''
            Gets postprocessing data from the composer
        '''
        try:
            post = self.composer.get_postprocessing_data()
            return post
        except NotImplementedError:
            # TODO better error handling
            print("Composer not set")
            return "ERROR" 

    def initialise_composer(self, layouts, executable):
        '''
            Setup steps on the composer
        '''
        arch = self._architectures.get_current_option()
        self.composer = arch.composer(layouts, list(executable.get_qubits()))
        self.composer.setup()

    def start_workers(
            self,
            entrypoint: callable,
            layouts: list,
        ):
        '''
            Starts the pool
            This is decoupled from initialisation to allow
             for worker swapping
        '''
        # Build communication queues
        self.construct_worker_queues()
        # Set the pool up
        self.pool = [
            self.ctx.Process(target=entrypoint,
                        name=f"PoolWorker{i}",
                        args=(
                            self.worker_task_queue,
                            self.worker_result_queue,
                            self.worker_comms_queue[i],
                            layouts
                        ),
                        daemon=True)
            for i in range(N_PROCESSES)
        ]

        for proc in self.pool:
            proc.start()
        self.pool_running = True

    def construct_worker_queues(self):
        '''
            Rebuilds communication queues for workers
        '''
        self.worker_task_queue = self.ctx.Queue()
        self.worker_comms_queue = [self.ctx.Queue(
                maxsize = 4
            )
            for _ in range(N_PROCESSES)
        ]
        self.worker_result_queue = self.ctx.Queue()

        # Manager object for worker callback
        self.worker_ipc = IPCManager(self.worker_result_queue)

    def run_task(self, task_queue=None, completion_queue=None, TIMEOUT=0.25):
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

        # Extract task from queue
        recv = task_queue.get(block=True, timeout=TIMEOUT)
        task_name, args, kwargs = recv 
        # Dispatch on task name
        task = self._tasks.get(task_name, None)
        if task is None:
            raise Exception(f"Unknown task: {task_name}")
        else:
            # Invoke the task
            result = task(self, *args, **kwargs)

            # If a response occurs, pass it back
            # Prepend the name of the task
            # This acts as an IPC handle
            if result is not None:
                completion_queue.put((task_name, result))

    def run_priority_task(self):
        '''
            Run a priority task
        '''
        return self.run_task(
            task_queue = self.manager_priority_task_queue,
            completion_queue = self.manager_completion_queue
        )

    def synchronise_rz_precision(self):
        '''
            Synchronise precision on workers
        '''
        self.broadcast_workers(
            rottnest_worker.SET_RZ_PRECISION,
            get_rz_precision()
        )

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

        self.post_result_queue()

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
    def run_sequence(self, *args):
        '''
            Returns true if exiting, none otherwise
        '''
        # If not running, start the workers
        if not self.pool_running:
            self._task_start_workers()

        self.run_seq_start = time.time()
        print("Manager job start time:", self.run_seq_start)

        self.n_submitted = 0
        self.n_received = 0
        self.n_error = 0

        # Synchronise precision with workers
        self.synchronise_rz_precision()

        self.sequencer_time = 0
        self.cache_time = 0

        # Submit all jobs provided by sequencer
        # This loop blocks when task queue is full

        ### CONTEXT SETUP
        arch_ids = args[0]

        architecture = self._architectures.get_current_option()
        executable = self._executables.get_current_option()

        # Pass layouts to composer
        layouts = LayoutProxy.get_layouts()

        # For now, just force all layouts to recompute mem bounds
        # against the new architecture
        LayoutProxy.force_proxy_refresh()

        self.initialise_composer(layouts, executable)

        # TODO : Make cache force flush a procedure
        PyliqtrParser.force_cache_flush()

        ### MAIN LOOP
        # NOTE : This also tries to call a cache flush with a tag set
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
            while not self.composer.complete() or self.n_received < self.n_submitted:
                # Trigger priority task check
                self.check_run_priority()
                self.check_priority_result()
                self.post_result_queue()

        except Exception as e:
            print(e)
            print(f"Aborting, sentinel secs reached at {self.n_received}/{self.n_submitted} received ({self.n_error} errors)")
            print(f"Unaccounted items: {self.n_submitted - self.n_received - self.n_error}")

        # Send totals
        self.send_total()
        self.send_total(symbols.END_COMPUTATION)

        # Pre-emptive polling
        self.manager_completion_queue.put((
            commands.POLL, PoolStatus.FINISHED
        ))
        self.set_status(PoolStatus.FINISHED)

        print("All Received")
        print("time:", time.time() - self.run_seq_start)
        return True

    def process_result_elem(self, wrapped_result: tuple):
        '''
        Blocking read from worker_result_queue and
            process result
        '''
        unit_id, result = wrapped_result

        result_obj = self.composer.compose_result(unit_id, result)

        # Composer takes result to reportable
        self.composer.receive(
            result_obj
        )

        self.manager_completion_queue.put(
            (commands.GET_RESULTS_STREAM, result_obj.to_runchart())
        )

        # TODO: Batch
        self.n_received += 1
        return

    def send_total(self, cu_id=TOTAL):
        '''
            Asynch sending of totals
        '''
        totals = self.composer.get_result().to_runchart()
        self.manager_completion_queue.put((commands.GET_CURRENT_RESULTS, totals))

    def get_current_results(self, *args, **kwargs):
        '''
            Sends the results
            Wrapper around send total
        '''
        return self.composer.stack_frames[0].result.to_runchart()

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
            res_obj = self.composer.cache_request(cache_obj)
            if res_obj is not False:
                self.manager_completion_queue.put((
                        commands.GET_RESULTS_STREAM,
                        res_obj.to_runchart(),
                ))

        self.cache_time += time.time() - cache_start

    def stop_workers(self, submit_priority_worker=False):
        '''
            Orders all workers to shut down
        '''
        if not self.pool_running:
            # Pool isn't running, skip
            return True

        self.broadcast_workers(
            rottnest_worker.SHUTDOWN,
            submit_priority_worker = submit_priority_worker
        )

        for i, proc in enumerate(self.pool):
            proc.join()

        self.pool = []
        self.pool_running = False

        # Nontrivial return statement
        return True

    def stop_priority_worker(self):
        '''
            Sends a shutdown signal to the priority worker
        '''
        self.submit_priority(rottnest_worker.SHUTDOWN)
        #self.priority_process.join()
        return True


    ###
    # WORKER MANAGEMENT FUNCTIONS
    ###

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
        result = self.worker_ipc.get_item(
            rottnest_worker.EXEC_COMPUTE_UNIT
        )
        while result is not IPCManager.NOT_FOUND:
            self.process_result_elem(result)
            result = self.worker_ipc.get_item(
                rottnest_worker.EXEC_COMPUTE_UNIT
            )
        return

    def process_elem_obj(
        self,
        obj: "ComputeUnit",
    ):
        '''
            Triggers compilation of a compute unit
        '''
        self.submit_time = time.time()

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
                self.submit_worker_task(
                    rottnest_worker.EXEC_COMPUTE_UNIT,
                    obj
                )
                submitted = True
            else:
                # TODO: futex if possible
                print('Queue Full')
                # Wait for space in queue
                time.sleep(0.1)

        self.n_submitted += 1

    def check_restart_priority_worker(self):

        arch = self._architectures.get_current_architecture()
        worker_entrypoint = arch.worker_entrypoint

        if self.priority_process.exitcode is not None:
            # Process died
            self.priority_error_count += 1
            self.priority_process.join()
            self.priority_process = self.ctx.Process(target=worker_entrypoint,
                                name="PoolWorker(Priority) [RESTART]",
                                args=(self.priority_task_queue, self.priority_result_queue),
                                daemon=True)
            self.priority_process.start()


    def check_run_priority(self):
        '''
            Convenience function
        '''
        if not self.manager_priority_task_queue.empty():
            self.run_priority_task()

    def check_priority_result(self):
        # Check if process is alive
        # TODO
        #self.check_restart_priority_worker()

        while self.priority_error_count + self.priority_received_count < self.priority_submitted_count or not self.priority_result_queue.empty():
            try:
                result = self.priority_result_queue.get_nowait()
                self.priority_received_count += 1

                self.manager_completion_queue.put(result)
            except queue.Empty:
                break

def entrypoint(*args, **kwargs):
    '''
        Dispatch method
    '''
    return ComputeUnitExecutorPoolManager.entrypoint(*args, **kwargs)

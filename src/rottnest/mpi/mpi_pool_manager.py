import time

from collections import defaultdict

from rottnest.mpi.mpi_queue import MPIRootQueue

from rottnest.architecture_interface import rottnest_worker
from rottnest.process_pool import commands, symbols
from rottnest.process_pool.pool_manager import ComputeUnitExecutorPoolManager
from rottnest.architecture_interface.rottnest_worker import HALT
from rottnest.rz_decomposer.rz_decomposer import DEFAULT_PRECISION
from rottnest.config import REPORT_INTERVAL, RESULT_INTERVAL


class MPIPoolManager(ComputeUnitExecutorPoolManager):
    '''
        Manages communication (via MPI) with worker peers.

        Specifically, uses MPI's default peer system (ie. fixed pool at launch).
        This means certain features of the base PoolManager are disabled (eg.
        this cannot restart workers, as they are managed via MPI, not internally)
    '''

    def __init__(self, allocated_workers, allocated_priority_workers,
                 manager_task_queue, manager_completion_queue,
                 manager_priority_task_queue, manager_priority_completion_queue,
                 comm, worker=None):
        # ------ Same as base ------
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

        # Entrypoints
        self._architecture = None
        self.pool = list()
        self.priority_process = None

        self.manager_running = True

        self.priority_submitted_count = 0
        self.priority_received_count = 0
        self.priority_error_count = 0

        # Default precision
        self.precision_bits = 10

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
        # ------ Same as base ------

        # CHANGE : The pool is running by default when using MPI
        self.pool_running = True

        # CHANGE : These are no longer assumed to be multiprocessing queues,
        # and thus may not have file descriptors
        # Manager Communication queues
        self.manager_task_queue = manager_task_queue
        self.manager_completion_queue = manager_completion_queue

        # Dedicated priority task queue
        self.manager_priority_task_queue = manager_priority_task_queue
        self.manager_priority_completion_queue = manager_priority_completion_queue

        # We may not have a "_reader"
        # (eg. rottnest_mpi uses base queues, not MP queues)
        try:
            self.manager_task_fds = [
                self.manager_task_queue._reader,
                self.manager_priority_task_queue._reader,
                self.priority_result_queue._reader
            ]
        except AttributeError as e:
            # NOTE: If we have no FDs, then `main_loop()` will block, and not be usable
            self.manager_task_fds = []

        # Allocate last worker as priority, all else as standard
        # Here, MPIRootQueue is 2-way
        # (ie. put(x), get() will not give back x)
        self.priority_task_queue = MPIRootQueue(
            comm,
            priority=True,
            allocated_clients=allocated_priority_workers
        )
        self.priority_result_queue = self.priority_task_queue

        self.worker_task_queue = MPIRootQueue(
            comm,
            allocated_clients=allocated_workers
        )
        self.worker_result_queue = self.worker_task_queue



    # ---=[ Overriding Internals ]=---
    def _task_stop_workers(self):
        if not self.pool_running:
            return

        self.worker_task_queue.putall((HALT,))
        self.priority_task_queue.putall((HALT,))
        self.pool_running = False


    def process_elem_obj(self, obj: 'ComputeUnit'):
        '''
            Triggers compilation of a compute unit

            Largely the same as base, but replaces plain sleeping with a polling
            sleep that can detect available clients (and queue received data for
            later handling, freeing up network buffers)
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

        submitted = False
        while not submitted:
            # Spin until either we get a priority task or we are unblocked on the worker task

            self.check_run_priority()
            self.check_priority_result()

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
                # ---- CHANGE : poll queue rather than sleep ----
                self.worker_result_queue.poll(block=True, timeout=0.1)
                # ---- CHANGE -----------------------------------

        print("Submitted", self.n_submitted)
        self.n_submitted += 1


    def check_run_priority(self):
        global saved_architectures

        while not self.manager_priority_task_queue.empty():
            # Get task
            task, args = self.manager_priority_task_queue.get() # This should not block, now that we checked

            if task == "run_priority":
                print("manager got priority task", task, args)

                # CHANGE : Removed restart that is not possible with MPI

                # Submit task
                self.priority_task_queue.put(args)
                print("submitted priority", self.priority_submitted_count)
                self.priority_submitted_count += 1
            elif task == "save_arch":
                arch_id, arch_json_obj = args
                saved_architectures[arch_id] = arch_json_obj


    def check_priority_result(self):
        # CHANGE : Removed restart that is not possible with MPI

        while self.priority_error_count + self.priority_received_count < self.priority_submitted_count or not self.priority_result_queue.empty():
            try:
                result = self.priority_result_queue.get_nowait()
                print("received priority", self.priority_received_count)
                self.priority_received_count += 1

                self.manager_priority_completion_queue.put(result)
            except queue.Empty:
                break


    def _task_start_workers(self, *args):
        raise NotImplementedError("MPI-based managers cannot spawn their own workers")


    def restart_dead_processes(self):
        raise NotImplementedError("MPI-based managers cannot restart their own workers")


    def check_restart_priority_worker(self):
        raise NotImplementedError("MPI-based managers cannot restart their own workers")




'''
    Rottnest Worker Interface
'''

import abc

import multiprocessing as mp

from ..compute_units.layout_proxy import LayoutProxy
from cabaliser.widget import Widget

# Commands as constants
# Load from this location to prevent duplication

PING = 'ping'
PONG = 'pong'
SET_RZ_PRECISION = 'set_rz_precision'
EXEC_COMPUTE_UNIT  = 'exec_compute_unit'
EXEC_GRAPH_STATE = 'exec_widget'
GET_GRAPH = 'get_graph'
LOAD_LAYOUT = 'load_layout'
HALT = 'halt'

from rottnest.rz_decomposer.rz_decomposer import DEFAULT_PRECISION


# TODO: Replace with more generic decomposition manager

class RottnestWorker(abc.ABC):
    '''
        RottnestWorker
        Abstract base class defining an interface
        for Rottnest worker units
    '''
    def __init__(
            self,
            layouts=None,
            priority=False,
            blind=False,
            debug=None,
    ):

        self.running = True
        self._debug = debug
        self._priority = priority

        self._architecture_cache_table = {}

        self.worker_tasks = {
            PING: self.ping,
            SET_RZ_PRECISION: self.set_precision,
            EXEC_COMPUTE_UNIT: self.task_execute_compute_unit,
            EXEC_GRAPH_STATE: self.task_execute_graph_state,
            GET_GRAPH: self.get_graph,
            LOAD_LAYOUT: self.load_layout,
            HALT: self.halt
        }

        # Additional tasks for priority workers
        if self._priority:
            print("STARTING PRIORITY PROCESS")
            # In init import to avoid circular dependency issues
            from rottnest.priority_process import priority_worker_tasks 
            self.worker_tasks |= priority_worker_tasks

        # Workers enabled blinding
        # Architecture details are contained to workers
        if blind:
            self.worker_tasks[GET_GRAPH] = self.not_supported

        if layouts is not None:
            for layout_id, layout in layouts:
                self.worker_tasks[LOAD_LAYOUT](layout_id, layout)

    def __call__(
            self,
            task_queue: mp.Queue,
            worker_results_queue: mp.Queue,
            worker_comms_queue: mp.Queue,
            ):
        '''
            Dispatch method for the main worker loop
        '''
        return self.main(task_queue, worker_results_queue, worker_comms_queue)

    @classmethod
    def entrypoint(
            cls,
            task_queue: mp.Queue,
            worker_results_queue: mp.Queue,
            worker_comms_queue: mp.Queue,
            layouts=None,
            rz_precision=DEFAULT_PRECISION,
            priority=False,
            blind=False,
            debug=None,
        ):
        '''
            Default entrypoint function
            Invokes the dispatch call
        '''

        worker = cls(
            layouts=layouts,
            priority=priority,
            blind=blind,
            debug=debug
        )

        worker(task_queue, worker_results_queue, worker_comms_queue)

    def main(self, task_queue: mp.Queue, worker_results_queue: mp.Queue, comms_queue: mp.Queue):
        '''
            Worker loop - queries
        '''
        if self._priority:
            self.priority_main(task_queue, worker_results_queue, comms_queue)
        
        print("Worker started:", mp.current_process().name, flush=True)
        self.running = True
        while self.running:

            if not comms_queue.empty():
                queue = comms_queue
            elif not task_queue.empty():
                queue = task_queue
            else:
                continue
            task, *args = queue.get()
            response = self.worker_tasks[task](*args)
            if response is not None:
                worker_results_queue.put(response)
        return

    def priority_main(self, task_queue: mp.Queue, worker_results_queue: mp.Queue, comms_queue: mp.Queue): 
        print("Worker started:", mp.current_process().name, flush=True)
        self.running = True
        while self.running:

            if not comms_queue.empty():
                queue = comms_queue
            elif not task_queue.empty():
                queue = task_queue
            else:
                continue
            task, *args = queue.get()
            response = (task, self.worker_tasks[task](*args))
            if response is not None:
                worker_results_queue.put(response)
        return


    def halt(
            self,
            *args,
        ):
        '''
           Halts the worker
        '''
        self.running = False

    def ping(
            self,
            *args,
        ) -> str:
        '''
            Ping function for worker alive status checking
        '''
        return PONG

    def set_precision(
            self,
            precision: int,
        ):
        '''
            Set the Rz decomposition precision for the workers
            :: precision : int :: Precision in bits
        '''
        self.get_rz_decomposer().set_precision(precision)

    def load_layout(self, layout_id: int, layout_json: dict):
        '''
            Loads an architecture to the cache table
            This intentionally does not expose the non-id
             loads to the worker
            Not marked as a task so that it can be
             called in single threaded mode
        '''
        LayoutProxy.add_layout_with_id(
            layout_id,
            layout_json
        )

    @staticmethod
    def get_layout(layout_id: int) -> dict | None:
        '''
            Loads an architecture from the cache table
            :: architecture_id : int :: Key for architecture
            Returns either an architecture object (or builder), or None if the key is invalid
        '''
        return LayoutProxy.get_layout(layout_id)

    def set_rz_decomposer(self, manager):
        '''
            Not Yet implemented
            Will be used to sync workers to a particular manager on start-up

            FEATURE: RzDecomposition
            Proxy the gs_instance through a class that can hotswap between
            different decomposers
        '''
        raise NotImplementedError

    def get_rz_decomposer(self):
        '''
            Gets the current decomposition manager
            As this may be executed in a subprocess the import is inlined
            Within the worker this is intended to be a
            singleton method
        '''
        raise NotImplementedError

    def task_execute_compute_unit(
            self,
            compute_unit: "ComputeUnit",
        ) -> dict:
        '''
            Simple dispatch wrapper
        '''
        unit_id, result = self.execute_compute_unit(
            compute_unit
        ) 
        return unit_id, result.to_args()

    def execute_compute_unit(
            self,
            compute_unit: "ComputeUnit",
        ) -> dict:
        '''
            Executes a sequence of instructions
            This performs the graph state compilation
             on the worker
        '''
        unit_id = compute_unit.unit_id
        layout_id = compute_unit.layout_id
        widget = compute_unit.compile_graph_state()

        rz_tag_tracker = compute_unit.extract_rz_tracker()

        result = self.execute_graph_state(
            unit_id,
            layout_id,
            widget.json(),
            rz_tag_tracker.to_dict()
        )
        return unit_id, result

    def task_execute_graph_state( 
            self,
            unit_id: int,
            layout_id: int,
            widget: "Widget",
            rz_tag_tracker: "RzTagTracker"
        ) -> dict:
        '''
            Task wrapper to execute a graph state
            This handles return arguments
        '''
        return unit_id, self.execute_graph_state(
            unit_id,
            layout_id,
            widget,
            rz_tag_tracker
        ).to_args()

    def execute_graph_state(
            self,
            unit_id: int,
            layout_id: int,
            widget_json,
            rz_tag_tracker,
        ):
        '''
            Executes a graph node
            This performs the graph state
             compilation on the process pool,
             blinding the worker to the computation
        '''
        raise NotImplementedError

    def run_widget(
            self,
            cabaliser_obj,
            region_obj,
            rz_tag_tracker,
            full_output: bool=False
        ):
        '''
            Abstract base method
        '''
        raise NotImplementedError

    def get_stats(
            self,
            compiled_widget,
            compute_unit,
            cache_hash,
            ) -> dict:
        '''
            Abstract base method for extracting
            relevant statistics from a compiled
            widget
        '''
        raise NotImplementedError

    ###
    # Priority Worker Methods
    ###

    def execute_compute_unit_visualiser(
        self,
        compute_unit: "ComputeUnit"
        ) -> dict:
        '''
            This is a task for the architecture
        '''
        raise NotImplementedError 


    def get_graph(
            self,
            *args,
        ):
        '''
            Synchronises back end graph object unrolling with front end objects
            TODO: Replace
        '''
        raise NotImplementedError


    @staticmethod
    def __MISSING() -> dict:
        return {
            'cu_id': "MISSING",
            'status': 'fatal',
        }

    @staticmethod
    def __FAILED(
            error,
            traceback,
            compute_unit: "ComputeUnit",
            cache_hash: str,
            unit_id = None,
            ) -> dict:
        if unit_id is None:
            unit_id = getattr(
                    compute_unit,
                    "unit_id",
                    "ERROR"
                )
        return {
            'cu_id': str(unit_id),
            'err_type': repr(error),
            'traceback': traceback,
            'status': 'error',
        }

    def not_supported(self, *args):
        return 'Operation Not Supported'

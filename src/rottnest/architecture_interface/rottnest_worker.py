'''
    Rottnest Worker Interface
'''

import abc

import multiprocessing as mp
import traceback
import time

from ..input_parsers.rz_tag_tracker import RzTagTracker
from ..compute_units.compute_unit import ComputeUnit

from cabaliser.widget import Widget
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import saved_architectures
from rottnest.compute_units.layout_proxy import LayoutProxy

PING = 'ping'
PONG = 'pong'
SET_PRECISION = 'set_precision' 
EXEC_COMPUTE_UNIT  = 'exec_compute_unit'
EXEC_GRAPH_STATE = 'exec_widget'
GET_GRAPH = 'get_graph'
LOAD_LAYOUT = 'load_architecture'

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
            SET_PRECISION: self.set_precision,
            EXEC_COMPUTE_UNIT: self.execute_compute_unit,
            EXEC_GRAPH_STATE: self.execute_graph_state,
            GET_GRAPH: self.get_graph,
            LOAD_LAYOUT: self.load_layout,
        }

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
            ):
        '''
            Dispatch method for the main worker loop 
        '''
        return self.main(task_queue, worker_results_queue)

    @classmethod
    def entrypoint(
            cls,
            task_queue: mp.Queue,
            worker_results_queue: mp.Queue,
            layouts=None,
            priority=False,
            blind=False,
            debug=None,
        ):
        '''
            Default entrypoint function
            Invokes the dispatch call 
        '''

        worker = cls(layouts=layouts, priority=priority, blind=blind, debug=debug)
        worker(task_queue, worker_results_queue)

    def main(self, task_queue: mp.Queue, worker_results_queue: mp.Queue):
        '''
            Worker loop - queries 
        '''
        print("Worker started:", mp.current_process().name, flush=True)
        self.running = True
        while self.running:
            task, *args = task_queue.get()
            print(task, "ARGS: ", args)
            response = self.worker_tasks[task](*args)
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
        self.get_rz_decomposition_manager().set_precision(precision)

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

    def get_layout(self, layout_id: int) -> dict | None:
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
        '''
        raise NotImplementedError
 
    @staticmethod
    def execute_compute_unit(
            unit_id: int,
            layout_id: int,
            instruction_sequence: "InstructionSequence",
            rz_tag_tracker: RzTagTracker,
        ):
        '''
            Executes a sequence of instructions 
            This performs the graph state compilation
             on the worker 
        '''
        raise NotImplementedError

    @staticmethod
    def execute_graph_state(
            unit_id: int,
            layout_id: int,
            widget: "Widget",
            rz_tag_tracker: RzTagTracker,
        ):
        '''
            Executes a graph node 
            This performs the graph state
             compilation on the process pool, 
             blinding the worker to the computation
        '''
        raise NotImplementedError

    @staticmethod
    def get_graph(
            *args,
        ):
        '''
            Synchronises back end graph object unrolling with front end objects
            TODO: Replace
        '''
        raise NotImplementedError

    @staticmethod
    def run_widget(
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
            compute_unit: ComputeUnit,
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

    def not_supported(self):
        return 'Operation Not Supported' 

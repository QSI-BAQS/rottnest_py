'''
    Rottnest Worker Interface
'''

import abc

import multiprocessing as mp
import traceback
import time

from ..input_parsers.rz_tag_tracker import RzTagTracker


from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import saved_architectures


# TODO: Replace with more generic decomposition manager

class RottnestWorker(abc.ABC):
    '''
        RottnestWorker
        Abstract base class defining an interface
        for Rottnest worker units
    '''
    def __init__(self, debug=None, priority=False, blind=False):

        self.running = True
        self._debug = debug

        self._architecture_cache_table = {}

        self.worker_tasks = {
            'ping': self.ping,
            'set_precision': self.set_precision,
            'exec_compute_unit': self.execute_compute_unit,
            'exec_widget': self.execute_graph_node,
            'get_graph': self.get_graph,
            'load_architecture': self.load_architecture
        }

        # Workers enabled blinding
        # Architecture details are contained to workers
        if blind:
            self.worker_tasks['get_graph'] = self.not_supported 


    def __call__(
            self,
            task_queue: mp.Queue,
            worker_results_queue: mp.Queue,
            is_priority: bool = False
            ):
        '''
            Dispatch method for the main worker loop 
        '''
        return self.main(task_queue, worker_results_queue, is_priority=is_priority)

    @classmethod
    def entrypoint(cls, *args, **kwargs):
        '''
            Default entrypoint function
            Invokes the dispatch call 
        '''
        worker = cls()
        worker(*args, **kwargs)

    def main(self, task_queue: mp.Queue, worker_results_queue: mp.Queue, is_priority: bool = False):
        '''
            Worker loop - queries 
        '''
        print("Worker started:", mp.current_process().name, flush=True)
        self.running = True
        while self.running:
            task, *args = task_queue.get()
            response = worker_tasks[task](*args)
            if response is not None:
                worker_results_queue.put(response) 
        return       

    def halt(
            self,
            *args, 
            is_priority:bool = False
        ):
        '''
           Halts the worker 
        '''
        self.running = False

    def ping(
            self,
            *args, 
            is_priority:bool = False
        ) -> str:
        '''
            Ping function for worker alive status checking 
        '''
        return 'pong'

    def set_precision(
        self,
        precision: int,
        is_priority: bool = False):
        '''
            Set the Rz decomposition precision for the workers
            :: precision : int :: Precision in bits
        '''
        self.get_rz_decomposition_manager().set_precision(precision)

    def load_architecture(self, architecture_id: int, architecture_json: dict):
        '''
            Loads an architecture to the cache table
        '''
        self._architecture_cache_table[architecture_id] = architecture_json 

    def get_architecture(self, architecture_id: int) -> dict | None:
        '''
            Loads an architecture from the cache table 
            :: architecture_id : int :: Key for architecture
            Returns either an architecture object (or builder), or None if the key is invalid
        '''
        return self._architecture_cache_table.get(architecture_id, None)


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
            compute_unit: ComputeUnit,
            rz_tag_tracker: RzTagTracker,
            full_output: bool,
            cache_hash: str,
            is_priority: bool = False
        ):
        '''
            Executes compute unit
        '''
        raise NotImplementedError

    @staticmethod
    def execute_graph_node(
            compute_unit: ComputeUnit,
            rz_tag_tracker: RzTagTracker,
            full_output: bool,
            cache_hash: str,
            is_priority: bool = False
        ):
        '''
            Executes compute unit
        '''
        raise NotImplementedError



    @staticmethod
    def get_graph(
            *args,
            is_priority: bool = False
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

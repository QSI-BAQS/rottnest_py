'''
    Rottnest Worker Interface
'''

import abc

from rottnest.compute_units.compute_unit import ComputeUnit
import multiprocessing as mp
import traceback
import time

from rottnest.server.model.graph_view import get_graph
from rottnest.server.model.graph_view import view_cache
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker
from rottnest.compute_units.architecture_proxy import saved_architectures
from rottnest.input_parsers import pyliqtr_parser

# TODO: Replace with more generic decomposition manager
from rottnest.gridsynth.gridsynth import gs_instance

class RottnestWorker(abc.ABC):
    '''
        RottnestWorker
        Abstract base class defining an interface
        for Rottnest worker units
    '''
    def __init__(self, debug=None, priority=False):

        self.running = True
        self._debug = debug

        self.worker_tasks = {
            'ping': self.ping,
            'set_precision': self.set_precision,
            'exec_cu': self.exec_compute_unit,
            'get_graph': self.get_graph,
            'exec_graph_node': self.exec_graph_node
        }

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

    def main(self, task_queue: mp.Queue, worker_results_queue: mp.Queue, is_priority: bool = False):
        '''
            Worker loop - queries 
        '''
        print("Worker started:", mp.current_process().name, flush=True)
        self.running = True
        while self.running:
            task, *args = task_queue.get()
            worker_tasks[task](worker_results_queue, *args)
        return       

    def halt(
            self,
            worker_results_queue,
            *args, 
            is_priority:bool = False
        ):
        '''
           Halts the worker 
        '''
        self.running = False

    def ping(
            self,
            worker_results_queue,
            *args, 
            is_priority:bool = False
        ):
        '''
            Ping function for worker alive status checking 
        '''
        worker_results_queue.put('pong') 


    def set_debug(self, is_priority):
        if not is_priority:
            stdout = open('/dev/null', 'w')
            sys.stdout = f
            old_stdout = sys.stdout # Disable printing
        else:
            old_stdout = sys.stdout

    def set_precision(
        self,
        worker_results_queue,
        *args,
        is_priority: bool = False):
    '''
        Set the precision for the workers
    '''
    precision = int(args[0])
    gs_instance.set_precision(precision)

    @staticmethod
    def exec_compute_unit(
            worker_results_queue,
            *args,
            is_priority: bool = False
        ):

    try:
        compute_unit, rz_tag_tracker, full_output, cache_hash, np_qubits = args
        compute_unit: ComputeUnit

        stats = {
            'cu_id': compute_unit.unit_id,
            'status': 'running',
            'cache_hash': cache_hash,
        }

        arch_json_obj = compute_unit.get_architecture_json()

        # worker_results_queue.put(stats.copy())

        widget = compute_unit.compile_graph_state()

        print("compile done", flush=True, file=old_stdout)

        # Debug output widget outputs
        if is_priority:
            with open('debug_obj.json', 'w') as f:
                print(widget.json(), file=f)

        orch = run_widget(
             cabaliser_obj=widget.json(),
             region_obj=arch_json_obj,
             full_output=full_output,
             rz_tag_tracker=rz_tag_tracker
        )
        
        stats = {
            'volumes': orch.get_space_time_volume(),
            't_source': orch.get_T_stats(),
            'tocks': orch.get_tock_stats(),
            'vis_obj': None,
            'cu_id': compute_unit.unit_id,
            'status': 'complete',
            'cache_hash': cache_hash,
            'np_qubits': np_qubits,
        }

        stats['tocks']['total'] = sum(stats['tocks'].values())
        

        if full_output:
            stats['vis_obj'] = orch.json
        
        print("storing result", flush=True, file=old_stdout)

        worker_results_queue.put(stats)

    except Exception as e:
        tb = traceback.format_exception(e)
        try:
            # Debug output exceptions
            with open('errors.out', 'a') as f:
                print('=============file===========', file=f)
                print(widget.json(), file=f)
                print('=============tb===========', file=f)
                print(''.join(tb), file=f)
        except:
            pass

        try:
            composer.get_stats()
            stats = {
                'cu_id': str(getattr(compute_unit, "unit_id", "ERROR")), 
                'err_type': repr(e), 
                'traceback': tb,
                'status': 'error',
                'cache_hash': cache_hash,
                'np_qubits': np_qubits,
            }
        except:
            stats = {
                'cu_id': "MISSING",
                'status': 'fatal',
            }

        worker_results_queue.put(stats)
    finally:
        sys.stdout = old_stdout

    @staticmethod
    def worker_get_graph(
            worker_results_queue,
            *args,
            is_priority: bool = False
        ):
        '''
            Synchronises back end graph object unrolling with front end objects
            TODO: Replace
        '''
        try:
            worker_results_queue.put(get_graph(args[0]))
        except:
            traceback.print_exc()
            worker_results_queue.put('ERROR')

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

    @staticmethod
    def get_stats(compiled_unit, compute_unit) -> dict:
        '''
            Abstract base method for extracting
            relevant statistics from a compiled
            widget 
        '''
        pass

    @staticmethod
    def __MISSING -> dict:

                    stats = {
                    'cu_id': "MISSING",
                    'status': 'fatal',
                }

    @staticmethod
    def __FAILED(
            error,
            traceback,
            compute_unit,
            cache_hash,
            np_qubits,
            ) -> dict:
        stats = {
                'cu_id': str(
                    getattr(
                        compute_unit,
                        "unit_id",
                         "ERROR"
                    )
                ), 
                'err_type': repr(error), 
                'traceback': traceback,
                'status': 'error',
                'cache_hash': cache_hash,
                'np_qubits': np_qubits,
                }
            except:


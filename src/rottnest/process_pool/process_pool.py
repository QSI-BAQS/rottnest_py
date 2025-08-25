from enum import Enum, auto
import multiprocessing as mp
from threading import Thread

from typing import Any
from types import GeneratorType

import time 
import queue
import select
from copy import deepcopy

from collections import defaultdict, deque

from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers import pyliqtr_parser


from rottnest.plugins import architectures, executables

#from rottnest.process_pool.process_worker import pool_worker_main
#from rottnest.executables.current_executable import current_executable


from rottnest.input_parsers.cirq_parser import shared_rz_tag_tracker
 
from rottnest.architecture_interface.rottnest_worker import RottnestWorker

# TODO: Move these to an appropriate config

from .pool_manager import ComputeUnitExecutorPoolManager

from rottnest.config import N_PROCESSES, SEGFAULT_SENTINEL_TIMEOUT_SECS

from .symbols import TOTAL, SPAWN_CONTEXT
from rottnest.process_pool import commands, symbols

# result_manager = mp.Manager()
# dummy_result_cache = result_manager.dict()

class ComputeUnitExecutorPool:    
    '''
        This class acts as an interface to the worker 
         pool manager
        Function calls here bind to calls to the manager 
         queue 
        The manager is then responsible for dispatching   
         tasks to elements in the queue 
        This gives a singleton interface for the queue
         and allows the manager to run on a separate process 
        It is not intended that any serious computation 
         occur in this class, as it will be bound to the             front end server's event loop, and so computation
         should be delegated to the manager 
    '''

    @staticmethod
    def _generate_compute_units(
            layout_ids: list[int],
            architecture: 'RottnestArchitecture',
            executable: 'RottnestExecutable'
        ) -> GeneratorType:
        '''
            Generates compute units for distribution 
            This forms a producer / consumer pattern 
        '''
        # Drops cache if the architecture changes
        pyliqtr_parser.set_cache_tag(layout_ids)

        parser = PyliqtrParser(executable())
        parser.parse()
        
        seq = Sequencer(layout_ids)
        it = seq.sequence_pyliqtr(parser)

        return it

    def _generate_graph_states(
            layout_ids: list[int],
            architecture: 'RottnestArchitecture',
            executable: 'RottnestExecutable'
        ) -> GeneratorType:
            '''
                Generates graph states for distribution
            '''
            ...


#    @staticmethod
#    def _run_sequence(
#            arch_ids: list[int],
#            architecture: 'RottnestArchitecture',
#            executable: 'RottnestExecutable'
#        ) -> GeneratorType:
#
#        # Drops cache if the architecture changes
#        pyliqtr_parser.set_cache_tag(arch_ids)
#
#        # TODO: De-hard code this at some point
#        global saved_architectures
#
#        # Triggers parsing of pyliqtr
#        parser = PyliqtrParser(executable)
#        parser.parse()
#       
#        # Sequences over the architectures
#        # This should eventually be hooked for more complex sequencers
#        seq = Sequencer(*arch_ids)
#    
#        # Gate iterator
#        it = seq.sequence_pyliqtr(parser)
#
#        # Yields (compute_unit, rz_tag_tracker, full_output)
#        wrapped_it = ((obj, shared_rz_tag_tracker, False) for obj in it)
#
#        print("iterator generation done")
#
#        return wrapped_it

    def __init__(self):
        self.ctx = mp.get_context(SPAWN_CONTEXT)
        self.manager_task_queue = self.ctx.Queue()
        self.manager_completion_queue = self.ctx.Queue()
        self.manager_priority_task_queue = self.ctx.Queue()
        self.manager_priority_completion_queue = self.ctx.Queue()

    def start(self):
        self.manager = self.ctx.Process(
            target=ComputeUnitExecutorPoolManager.entrypoint, 
            args=[
                 self.manager_task_queue, 
                 self.manager_completion_queue,
                 self.manager_priority_task_queue,
                 self.manager_priority_completion_queue
            ],
            name="PoolManager"
        )
        self.manager.start()
        self.synchronise_modules()

    def synchronise_modules(self):
        '''
            Attempts to synchronise all architecure and 
            executable modules with the manager
        '''
        architecture_strings = (
            architectures.get_module_names()
            + architectures.get_loaded_filepaths()
        )
        executable_strings = (
            executables.get_module_names()
            + executables.get_loaded_filepaths()
        )
        self.manager_task_queue.put(
            (commands.SYNCHRONISE_MODULES,
            architecture_strings,
            executable_strings)
        )

    def start_workers(self):
        '''
           Spins up the workers 
        '''
        self.manager_task_queue.put(
            (commands.START_WORKERS,)
        )

    def stop_workers(self):
        '''
           Spins down the workers 
        '''
        self.manager_task_queue.put(
            (commands.STOP_WORKERS,)
        )

    def set_architecture_module(
                self,
                architecture_module: str
            ):
        '''
            Sets the architecture module
            This is set on all the workers and the manager
        '''
        self.manager_task_queue.put(
            (
                commands.SET_ARCHITECTURE_MODULE,
                architecture_module 
            )
        )

    def set_executable(self, executable: str):
        '''
            Sets the current executable 
            This is only set on the manager
        '''
        self.manager_task_queue.put(
            (
                commands.SET_EXECUTABLE,
                executable 
            )
        )

    def set_executable_params(self, params: dict):
        '''
            Sets the parameters for the executable
            This is only set on the manager
        '''
        self.manager_task_queue.put(
            (
                commands.SET_EXECUTABLE_PARAMS,
                params 
            )
        )
 
    def run_sequence(self, layout_ids):
        '''
            Puts a run sequence to the worker queue
        '''
        self.manager_task_queue.put(
            (
                commands.RUN_SEQUENCE,
                layout_ids
            )
        )
   
    def shutdown(self):
        '''
            Broadcasts a shutdown to all workers
        '''
        self.manager_task_queue.put(
            (commands.TERMINATE,)
        )
   
    def ping_manager(self):
        '''
            Checks for worker life 
        '''
        self.manager_task_queue.put((commands.PING_MANAGER,))
        resp = self.manager_completion_queue.get() 
        assert resp == symbols.PONG 
 
    def ping(self):
        '''
            Checks for worker life 
        '''
        self.manager_task_queue.put((commands.PING,))
        resp = self.manager_completion_queue.get() 
        assert resp == symbols.PONG 

 
    def run_priority(self, compute_unit, rz_tag_tracker, full_output=True):
        self.manager_priority_task_queue.put(("run_priority", ('exc_cu', compute_unit, rz_tag_tracker, full_output, [None], 0)))

    
    def run_priority_graph_node(self, node_name, arch_obj):
        self.manager_priority_task_queue.put(("run_priority", ('exc_graph_node', node_name, arch_obj)))

    def save_arch(self, arch_id, arch_json_obj):
        self.manager_priority_task_queue.put(("save_arch", (arch_id, arch_json_obj)))

    def get_graph(self, graph_id):
        self.manager_priority_task_queue.put(("run_priority", ('get_graph', graph_id)))

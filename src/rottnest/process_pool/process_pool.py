'''
    Process pool controller
    Holds high level API calls to manager systems
    The manager lives on a separate process and handles asynch
    This class provides a non-asynch interface 
'''
import multiprocessing as mp

from types import GeneratorType

from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

from rottnest.process_pool import commands, symbols
from rottnest.priority_process import commands as priority_commands

from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.plugins import architectures, executables
from rottnest.rz_decomposer import get_rz_precision


from .single_instantiation import SingleInstantiation
from .status_decorator import status_update, StatusTracked  
from .pool_manager import ComputeUnitExecutorPoolManager

from .symbols import TOTAL, SPAWN_CONTEXT

from .pool_status import PoolStatus
from .ipc_manager import IPCManager


class ComputeUnitExecutorPool(StatusTracked, SingleInstantiation):
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
         occur in this class, as it will be bound to the             
         front end server's event loop, and so computation
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
        PyliqtrParser.set_cache_tag(layout_ids)

        parser = PyliqtrParser(executable())
        parser.parse()

        seq = Sequencer(layout_ids)
        it = seq.sequence_pyliqtr(parser)

        return it

    @staticmethod
    def _generate_graph_states(
            layout_ids: list[int],
            architecture: 'RottnestArchitecture',
            executable: 'RottnestExecutable'
        ) -> GeneratorType:
        '''
            Generates graph states for distribution
        '''
        ...

    def __init__(self):
        '''
            Constructor
        '''

        self.ctx = mp.get_context(SPAWN_CONTEXT)
        
        self.manager = None

        self.manager_task_queue = self.ctx.Queue()
        self.manager_completion_queue = self.ctx.Queue()
        self.manager_priority_task_queue = self.ctx.Queue()

        # TODO: Scope removal
        self.manager_priority_completion_queue = self.ctx.Queue()

        self._status = PoolStatus.UNSTARTED 

        self.ipc = IPCManager(self.manager_completion_queue) 

        # TODO: Scope removal
        #self.priority_ipc = IPCManager(self.manager_completion_queue) 


    def get_status(self):
        '''
            Getter for the current status of the pool
        '''
        return self._status

    def set_status(self, status):
        '''
            Setter for the current status of the pool
        '''
        self._status = status

    @status_update(
        PoolStatus.STARTING,
        PoolStatus.STARTED
    )
    def start(self):
        '''
            Starts the process pool manager
        '''
        # If manager is already running, do not start another
        if self.manager is None:

            from rottnest.process_pool.entrypoints import pool_manager 

            # This call should validate the execution
            # context
            entrypoint = pool_manager.get_entrypoint()

            self.manager = self.ctx.Process(
                target=entrypoint,
                args=[
                     self.manager_task_queue,
                     self.manager_completion_queue,
                     self.manager_priority_task_queue,
                     self.manager_priority_completion_queue
                ],
                name="PoolManager"
            )
            self.manager.start()

        # Open with a module synch
        self.synchronise_modules()

    ###
    # State synchronisation methods 
    ###

    @status_update(
        PoolStatus.SYNCHRONISING, 
        PoolStatus.SYNCHRONISED
    )
    def synchronise(self):
        '''
            Wrapper synchronisation function
        '''
        self.synchronise_modules()
        self.synchronise_options()
        self.synchronise_rz_precision()
        self.synchronise_layouts()

    def synchronise_modules(self):
        '''
            Attempts to synchronise all architecure and
            executable modules with the manager
        '''
        self.manager_priority_task_queue.put(
            (
                commands.SYNCHRONISE_MODULES,
                architectures.get_synchronisation_strings(),
                executables.get_synchronisation_strings()
            )
        )
        return

    def synchronise_options(self):
        '''
            Synchronises from singletons
            TODO: extension for architecture 
                options goes here
        '''
        # Synch architecture
        architecture = architectures.get_current_architecture()
        self.set_architecture_module(architecture.get_name())

        # Synch executable
        executable = executables.get_current_executable()
        self.set_executable(executable.get_name())

        # Synch parameters
        executable_params = executables.get_executable_params()
        self.set_executable_params(executable_params)

    def synchronise_rz_precision(self):
        '''
            Synchronises the Rz precision with the queue
        '''
        precision = get_rz_precision()
        self.manager_priority_task_queue.put(
            (
                commands.SET_RZ_PRECISION,
                precision
            )
        )
        return

    def synchronise_layouts(self):
        '''
            Synchronises all loaded layouts with the
            manager
        '''
        layout_payload = list(LayoutProxy.get_layouts())
        self.manager_priority_task_queue.put(
            (
                commands.SYNCHRONISE_LAYOUTS,
                layout_payload
            )
        )
        return

    ###
    # Worker control functions
    ###
    @status_update(
        PoolStatus.STARTING_WORKERS, 
        PoolStatus.STARTED_WORKERS
    )
    def start_workers(self):
        '''
           Spins up the workers
        '''
        self.manager_priority_task_queue.put(
            (commands.START_WORKERS,)
        )

    def stop_workers(self):
        '''
           Spins down the workers
        '''
        self.manager_priority_task_queue.put(
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
        self.manager_priority_task_queue.put(
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
        self.manager_priority_task_queue.put(
            (
                commands.SET_EXECUTABLE,
                executable
            )
        )

    def get_synchronisation_status(self) -> dict:
        '''
            Getter for worker and manager status
        '''
        self.manager_priority_task_queue.put((commands.SYNCHRONISATION_STATUS,))

        resp = self.ipc.fetch(
            commands.SYNCHRONISATION_STATUS,
            blocking = True
        )
        return resp


    def set_executable_params(self, params: dict):
        '''
            Sets the parameters for the executable
            This is only set on the manager
        '''
        self.manager_priority_task_queue.put(
            (
                commands.SET_EXECUTABLE_PARAMS,
                params
            )
        )

    @status_update(
        PoolStatus.EXECUTING, 
        PoolStatus.EXECUTING
    )
    def run_sequence(self, layout_ids):
        '''
            Puts a run sequence to the worker queue
        '''
        self.manager_priority_task_queue.put(
            (
                commands.RUN_SEQUENCE,
                layout_ids
            )
        )

    def poll(self):
        '''
            Checks the state of the running job
        '''
        self.manager_priority_task_queue.put((commands.POLL,))
        status = self.ipc.get_item(
            commands.POLL,
            blocking=True
        )
        return status 
    
    def complete(self):
        '''
            Checks if a job has finished
            # WARN: Deprecated
        '''
        status = self.ipc.fetch(
            symbols.END_COMPUTATION,
            blocking=False
        )
        return status == symbols.END_COMPUTATION

    def shutdown_workers(self):
        '''
            Broadcasts a shutdown to all workers
        '''
        self.manager_priority_task_queue.put(
            (commands.STOP_WORKERS,)
        )

    def shutdown_workers_status(self):
        '''
            Checks the status of a shutdown
        '''
        resp = self.ipc.get_item(
            commands.STOP_WORKERS,
            blocking=False
        )
        return resp is not IPCManager.NOT_FOUND

    def terminate(self):
        '''
            Broadcasts a shutdown to all workers
        '''
        self.manager_priority_task_queue.put(
            (commands.TERMINATE,)
        )



    def ping_manager(self):
        '''
            Checks for worker life
        '''
        self.manager_priority_task_queue.put((commands.PING_MANAGER,))
        # Assumes that it will be fetched shortly
        resp = self.ipc.fetch(
            commands.PING_MANAGER,
            blocking=True
        )
        assert resp == symbols.PONG

    def ping(self):
        '''
            Checks for worker life
        '''
        self.manager_priority_task_queue.put((commands.PING,))

        # Assumes that it will be fetched shortly
        resp = self.ipc.fetch(
            commands.PING,
            blocking=True
        )
        assert resp == symbols.PONG

    def get_results_stream(self, max_get=10):
        '''
            Gets current results stream objects
        '''
        collected = []
        count = 0
        while (count < max_get) and IPCManager.NOT_FOUND is not ( 
                resp := self.ipc.get_item(
                    commands.GET_RESULTS_STREAM
                )
            ):
            collected.append(resp)
        return collected 

    def get_results(self, blocking=False):
        '''
            Requests results from the pool manager 
        '''
        resp = self.ipc.batch_get(
            commands.GET_CURRENT_RESULTS
        )
        if resp is not IPCManager.NOT_FOUND: 
            '''
                Only need the most recent object
            '''
            return resp[-1]
    
        # Non-blocking update
        if not blocking:
            return [] 

        self.manager_task_queue.put(
            (commands.GET_CURRENT_RESULTS,)
        ) 
        resp = self.ipc.get_item(
            commands.GET_CURRENT_RESULTS,
            blocking=True
        )
        return resp

    def get_final_results(self):
        '''
            Gets final results
            This is only guaranteed to work if the 
            backend has stopped emitting results objects
        '''
        # Flush any remaining results
        self.ipc.flush()

        self.manager_task_queue.put(
            (commands.GET_CURRENT_RESULTS,)
        ) 

        results = self.ipc.batch_get(commands.GET_CURRENT_RESULTS)
        if results is not IPCManager.NOT_FOUND:
            return results[-1]

        resp = self.ipc.get_item(
            commands.GET_CURRENT_RESULTS,
            blocking=True
        )
        return resp

    def flush_results_cache(self):
        '''
            Clears buffers saving memory
        '''
        self.ipc.clear(commands.GET_CURRENT_RESULTS)
        self.ipc.clear(commands.GET_RESULTS_STREAM)

    def reset_execution_context(self): 
        '''
            Resets the execution context on the manager
        '''
        self.manager_task_queue.put(
            (commands.RESET_EXECUTION_CONTEXT,)
        ) 


    ###
    # PRIORITY PROCESS COMMANDS 
    ###

    def synchronise_priority_process(self):
        self.manager_priority_task_queue.put(
            (priority_commands.SYNCHRONISE_PRIORITY,)
        ) 


    def get_callgraph(self, graph_id):
        '''
            Sends and asynch request to 
        '''
        self.manager_priority_task_queue.put(
            (priority_commands.GET_CALLGRAPH, graph_id)
        ) 

    def get_callgraph_status(self):
        '''
            Gets a status object from the IPC
        '''
        status = self.ipc.get_item(
            priority_commands.GET_CALLGRAPH,
            blocking=False
        )
        if status is IPCManager.NOT_FOUND:
            return None
        return status 

    def clear_buffers(self):
        '''
            Reset all buffer state
        '''
        self.ipc.clear_all()


    def get_visualiser(self, graph_id):
        '''
            Sends and asynch request to get a visualiser object 
        '''
        self.manager_priority_task_queue.put(
            (priority_commands.GET_VISUALISER, graph_id)
        ) 

    def get_visualiser_next(self):
        '''
            Requests the next object in a sequence
        '''
        self.manager_priority_task_queue.put(
            (priority_commands.GET_VISUALISER_NEXT, graph_id)
        ) 

    def get_visualiser_status(self):
        '''
            Gets a status object from the IPC
            This batches both the base get and the
            get_next requests 
        '''
        status = self.ipc.get_item(
            priority_commands.GET_VISUALISER,
            blocking=False
        )
        if status is IPCManager.NOT_FOUND:
            status = self.ipc.get_item(
                priority_commands.GET_VISUALISER_NEXT,
                blocking=False
            )
            if status is IPCManager.NOT_FOUND:
                return None
        return status 

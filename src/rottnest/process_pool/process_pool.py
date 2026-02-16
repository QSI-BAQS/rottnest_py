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

from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.plugins import architectures, executables

from .status_decorator import status_update, StatusTracked  
from .pool_manager import ComputeUnitExecutorPoolManager

from .symbols import TOTAL, SPAWN_CONTEXT

from .pool_status import PoolStatus
from .ipc_manager import IPCManager


# result_manager = mp.Manager()
# dummy_result_cache = result_manager.dict()

class ComputeUnitExecutorPool(StatusTracked):
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
        self.manager_priority_completion_queue = self.ctx.Queue()

        self._status = PoolStatus.UNSTARTED 

        self.ipc = IPCManager(self.manager_completion_queue) 
        self.priority_ipc = IPCManager(self.manager_completion_queue) 


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

    def synchronise_options(self):
        '''
            Synchronises from singletons
        '''
        architecture = architectures.get_current_architecture()
        self.set_architecture_module(architecture.get_name())

        executable = executables.get_current_executable()
        self.set_executable(executable.get_name())

        # TODO: Fix this
        #executable_params = executables.get_executable_params()
        #self.set_exectuable_params(executable_params)



    def synch_and_start_from_singletons(self):
        '''
            Loads singleton parameters then launches the pool
        '''

        arch = architectures.get_current_architecture()
        arch_params = executables.get_current_executable_args()

        executable = executables.get_current_executable()
        exec_params = executables.get_current_executable_args()
        layouts = LayoutProxy.get_layouts()

        self.synch_and_start(arch, executable, layouts, executable_params=exec_params)


    def synch_and_start(
        self,
        architecture: "RottnestArchitecture",
        executable: "RottnestExecutable",
        layouts: dict,
        *,
        architecture_params: dict = None,
        executable_params: dict = None,
        ):
        '''
            Wraps the synchronisation and start functions
        '''

    @status_update(
        PoolStatus.STARTING,
        PoolStatus.STARTED
    )
    def start(self):
        '''
            Starts the process pool manager
        '''
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

    @status_update(
        PoolStatus.SYNCHRONISING, 
        PoolStatus.SYNCHRONISED
    )
    def synchronise(self):
        '''
            Wrapper synchronisation function
        '''
        self.synchronise_modules_and_layouts()
        self.synchronise_options()
        # TODO:
        # self.synchronise_precision

    def synchronise_modules_and_layouts(self):
        '''
            Calls synchronisation functions
        '''
        self.synchronise_modules()
        self.synchronise_layouts()

    def synchronise_modules(self):
        '''
            Attempts to synchronise all architecure and
            executable modules with the manager
        '''
        self.manager_task_queue.put(
            (
    commands.SYNCHRONISE_MODULES,
    architectures.get_synchronisation_strings(),
    executables.get_synchronisation_strings()
            )
        )
        return


    def synchronise_precision(self):
        '''
            Synchronises the Rz precision with the queue 
        '''
        prec = executables.get_precision()

        self.manager_task_queue.put(
            (
                commands.SET_PRECISION,
                prec
            )
        )
        return

    def synchronise_layouts(self):
        '''
            Synchronises all loaded layouts with the
            manager
        '''
        layout_payload = list(LayoutProxy.get_layouts())
        self.manager_task_queue.put(
            (
                commands.SYNCHRONISE_LAYOUTS,
                layout_payload
            )
        )
        return

    @status_update(
        PoolStatus.STARTING_WORKERS, 
        PoolStatus.STARTED_WORKERS
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
        self.synchronise_precision()

    def get_synchronisation_status(self) -> dict:
        '''
            Getter for worker and manager status
        '''
        self.manager_task_queue.put((commands.SYNCHRONISATION_STATUS,))

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
        self.manager_task_queue.put(
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
        self.manager_task_queue.put(
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
        print("POLLING POOL")
        status = self.ipc.get_item(
            commands.POLL,
            blocking=True
        )
        print("STATUS", status)
        return status 
    
    def complete(self):
        '''
            Checks if a job has finished
        '''
        status = self.ipc.fetch(
            symbols.END_COMPUTATION,
            blocking=False
        )
        return status == symbols.END_COMPUTATION


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
        self.manager_task_queue.put((commands.PING,))

        # Assumes that it will be fetched shortly
        resp = self.ipc.fetch(
            commands.PING,
            blocking=True
        )
        assert resp == symbols.PONG

    def get_results(self):
        '''
            Requests results from the pool manager 
        '''
        resp = self.ipc.get_item(
            commands.GET_CURRENT_RESULTS
        )
        if resp is not IPCManager.NOT_FOUND: 
            return resp

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
        results = self.ipc.batch_get(commands.GET_CURRENT_RESULTS)
        if len(results) > 0:
            return results[-1]

        # Todo, make this stateful
        # At the moment the command gets dropped
        resp = self.ipc.get_item(
            commands.GET_CURRENT_RESULTS,
            blocking=True
        )
        return resp

    #######

    def run_priority(self, compute_unit, rz_tag_tracker, full_output=True):
        self.manager_priority_task_queue.put(("run_priority", ('exc_cu', compute_unit, rz_tag_tracker, full_output, [None], 0)))

    def run_priority_graph_node(self, node_name, arch_obj):
        self.manager_priority_task_queue.put(("run_priority", ('exc_graph_node', node_name, arch_obj)))

    def save_arch(self, arch_id, arch_json_obj):
        self.manager_priority_task_queue.put(("save_arch", (arch_id, arch_json_obj)))

    def get_graph(self, graph_id):
        self.manager_priority_task_queue.put(("run_priority", ('get_graph', graph_id)))

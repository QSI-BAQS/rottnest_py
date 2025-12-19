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

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    @status_update(
        PoolStatus.SYNCHRONISING, 
        PoolStatus.IDLE
    )
    def synch_from_singletons(self):
        '''
            Synchronises from singletons
        '''
        architecture = architectures.get_current_architecture()
        self._pool.set_architecture_module(architecture)

        executable = executables.get_current_executable()
        self._pool.set_executable(executable)

        executable_params = executables.get_executable_params()
        self._pool.set_exectuable_params(executable_params)



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
        PoolStatus.SYNCHRONISING,
        PoolStatus.IDLE
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

    def synchronise(self):
        '''
            Calls synchronisation functions
        '''
        self.synchronise_modules()
        self.synchronise_layouts()

    @status_update(
        PoolStatus.SYNCHRONISING, 
        PoolStatus.IDLE
    )
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

    @status_update(
        PoolStatus.SYNCHRONISING, 
        PoolStatus.IDLE
    )
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

    @status_update(
        PoolStatus.SYNCHRONISING, 
        PoolStatus.IDLE
    )
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
        print(layout_ids)
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
        # TODO - get status from backend

        self.manager_priority_task_queue.put((commands.POLL,))
        status = self.manager_priority_completion_queue.get()

        self.set_status(status)
        return status 
    

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

    def get_results(self):
        '''
            Testing function
            Requests results from the pool manager 
        '''
        self.manager_task_queue.put(
            (commands.GET_CURRENT_RESULTS,)
        ) 
        print("Awaiting")
        resp = self.manager_completion_queue.get()
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

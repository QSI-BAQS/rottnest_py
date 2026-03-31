from enum import Enum
from rottnest.procedures.stage import RottnestCompilerStage
from rottnest.server.app.application import RottnestApplication, \
    RottnestApplicationUnavailableException
from rottnest.debug.util import with_debug_log
from threading import Thread
import queue

class ProcedureExecutionStateTag(Enum):
    '''
       Tag for the execution state 
    '''
    INACTIVE = 1
    QUEUED = 2
    ACTIVE = 3


class ProcedureExecutionContext:
    '''
       When executing a procedure asynchronously, information about
       the context and what is being executed is worth knowing 
    '''

    def __init__(self, proc_id: int | None = None):
        self.proc_id = proc_id
        self.state_tag = ProcedureExecutionStateTag.INACTIVE

class ProcedureManager(RottnestCompilerStage):
    '''
        ProcedureManager class,
            * Single Instance object that will manage
            * procedures given to it of different qualities
               * async - Executed on a separate thread/process
               * sync  - Executed next in line within sync queue

            * Queue that ensures synchronised operation
              and management of the tasks to be done
            * Thread join handlers to ensure that the
              async tasks are managed appropriately
        In addition:
            * Dependency resolution of Procedures is required
              for the procedure to run properly.
    '''

    # class object for maintaining the current id
    NEXT_ID = 1

    # Singleton Instance
    _manager = None


    def __init__(self, app: RottnestApplication, \
                 track_stage_completion=False, queue_timeout=3):
        '''
           Initialises the manager
               * app - access to the application which has
                   access to the websockets that can be used
               * track_stage_completion - Debug field to see
                   what stages have been executed and when
                   they concluded
               * completed_tasks - list of tasks that have been
                   completed. Not used by default
        '''
        self.app = app
        self.id_set: set[int] = set()
        self.track_stage_completion = track_stage_completion
        self.queue_timeout = queue_timeout
        self.queued_tasks: queue.Queue[tuple[int, RottnestCompilerStage]] = queue.Queue()
        self.completed_tasks = list() # NOTE: NOT USED
        self.should_stop = False
        self.app_instance_is_uninit = False
        self.exec_context = ProcedureExecutionContext()

    @with_debug_log()
    def get_enqueued_size(self) -> int:
        '''
            Gets the number of elements currently enqueued
            within the procedure manager
        '''
        return len(self.id_set)
      
    @classmethod
    @with_debug_log()
    def get_instance(cls) -> type['ProcedureManager']:
        '''
           Singleton object that can be retrieved
           by the procedures

           _manager is the singleton instance here
        '''
        if ProcedureManager._manager is None:
            app = None # Just scoping it
            is_uninit = False
            try:
                app = RottnestApplication.get_instance()
            except RottnestApplicationUnavailableException as _e:
                app = RottnestApplication.get_uninitialised_instance()
                is_uninit = True

            ProcedureManager._manager = ProcedureManager(app)
            ProcedureManager._manager.app_instance_is_uninit = is_uninit
            
        return ProcedureManager._manager

    @with_debug_log()
    def execute_immediate(self, stage: RottnestCompilerStage):
        '''
           Executes the procedure immediately
           Return any data from the stage
        '''
        return stage.execute(self)

    @with_debug_log()
    def execute_defer(self, stage: RottnestCompilerStage):
        '''
           Defers the execution to the queue
               Will be executed when time is available 
        '''
        self.enqueue_procedure(stage)
        return True


    @with_debug_log()
    def stop_manager(self):
        '''
           Sets the `should_stop` field to True 
        '''
        self.should_stop = True
    
    @with_debug_log()
    def start_manager_in_thread(self) -> Thread:
        '''
           Will create a thread and invoke start_loop
           for it to run until the loop is meant to finish 
        '''
        def _thread_worker():
            self.start_loop()
            
        thread_joinhandler = Thread(target=_thread_worker, daemon=True)
        thread_joinhandler.start()
        return thread_joinhandler

    @with_debug_log()
    def dequeue_and_execute(self):
        '''
            Dequeue a procedure and execute it by also providing the
            manager as context
        '''
        id, proc = self.queued_tasks.get(True, self.queue_timeout)
        proc.execute(self)
        self.id_set.discard(id)
        self.queued_tasks.task_done()

    @with_debug_log()
    def start_loop(self):
        '''
           Starts te event loop, will await for tasks to be
           sent by producers and consumed by the manager
               - These are async procedures
        '''
        while not self.should_stop:
            # Blocks until 10 seconds and throws an exception
            # or has data available
            try:
                self.dequeue_and_execute()
            except queue.Empty:
                print("Timeout Reached or Invalid Queue Operation")
                pass

    @with_debug_log()
    def execute(self, compiler_environment=None,
                reporting=True,
                single_pass=False) -> bool | None:
        '''
           Overridden method that will start a procedure or stage
            with the manager available to access it

            None is returned by this method
        '''
        self.start_loop()
        return None
        
    @with_debug_log()
    def get_rottnest_application(self):
        '''
            Gets the rottnest application data that it has
            attached, this will icnlude websockets and plugins

            This is a safe wrapped for checking to see if
            application is now initialised
        '''
        retapp = self.app
        try:
            app_potentially_init = RottnestApplication.get_instance()
            self.app = app_potentially_init
            retapp = self.app
        except RottnestApplicationUnavailableException as _e:
            pass

        return retapp


    @with_debug_log()
    def get_active_procedure_ids(self):
        '''
           Retrieves a list of the current enqueued procedures
            - Note: Was originally going to be computed but we keep a dict
                for keeping track of them now
        '''
        return list(self.id_set)

    @with_debug_log()
    def enqueue_procedure(self, stage):
        '''
           Enqueues the procedure with a global id associated
           - This is a tuple 
        '''
        stage_id = ProcedureManager.next_global_id()
        id_stage_tuple = (stage_id, stage)
        self.id_set.add(stage_id)
        self.queued_tasks.put(id_stage_tuple)
    
    @classmethod
    @with_debug_log()
    def next_global_id(cls):
        '''
           Generates the next integer id - Class level object
        '''
        current = ProcedureManager.NEXT_ID
        ProcedureManager.NEXT_ID += 1
        return current

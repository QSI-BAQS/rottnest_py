from enum import Enum
from rottnest.procedures.stage import RottnestCompilerStage
from rottnest.server.app.application import RottnestApplication, \
    RottnestApplicationUnavailableException
from rottnest.debug.util import with_debug_log
from threading import Thread
import queue

class ProcedureEntityStateTag(Enum):
    '''
       Tag for the execution state 
    '''
    CONSTRUCTED = 1
    QUEUED = 2
    ACTIVE = 3
    COMPLETED = 4
    INVALID = -1

    


class ProcedureEntityTag:
    '''
       When executing a procedure asynchronously, information about
       the context and what is being executed is worth knowing 
    '''

    def __init__(self, proc_id: int = -1):
        '''
           Initialises the entity tag to be associated with the procedure 
        '''
        self.proc_id = proc_id
        self.state_tag = ProcedureEntityStateTag.CONSTRUCTED

    @classmethod
    def make(cls, proc_id: int):
        '''
           Constructing the procedure with a given procedure id
        '''
        return ProcedureEntityTag(proc_id)

    def progress_to_next_state(self):
        '''
           Progresses through the states based on the current state it is in
           Only when the state needs to be reset and usually that would result
           in a new procedure being constructed 
        '''
        if self.state_tag == ProcedureEntityStateTag.CONSTRUCTED:
            self.state_tag = ProcedureEntityStateTag.QUEUED
        elif self.state_tag == ProcedureEntityStateTag.QUEUED:
            self.state_tag = ProcedureEntityStateTag.ACTIVE            
        elif self.state_tag == ProcedureEntityStateTag.ACTIVE:
            self.state_tag = ProcedureEntityStateTag.COMPLETED

    def progress_to_active(self):
        '''
           For immediate execution mode, it will just jump from constructed to
           active 
        '''
        self.state_tag = ProcedureEntityStateTag.ACTIVE

    def set_state(self, state_tag: ProcedureEntityStateTag):
        '''
            Sets the current state tag for the execution
        '''
        self.state_tag = state_tag

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
        self.queued_id_set: set[int] = set()
        self.track_stage_completion = track_stage_completion
        self.queue_timeout = queue_timeout
        self.queued_tasks: queue.Queue[tuple[ProcedureEntityTag, RottnestCompilerStage]] = queue.Queue()

        # Used to keep track of completed tasks, however we will have a default
        # limit on how many we can track here
        self.completed_tasks = list() # NOTE: Not sure if we should use this or not

        

        # Provides an indicator if the application should stop, by default it is
        # considered active
        self.should_stop = False

        # Assumed not to be, however can be initialised via get_instance
        # to have an invalid RottnestApplication and will attempt to re-establish if
        # found to be in this state
        self.app_instance_is_uninit = False

        # Used to provide information regarding the current active procedure
        self.current_procedure_focus: tuple[ProcedureEntityTag, RottnestCompilerStage] = None

    @with_debug_log()
    def get_enqueued_size(self) -> int:
        '''
            Gets the number of elements currently enqueued
            within the procedure manager
        '''
        return len(self.queued_id_set)
      
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

           NOTE: It is assumed that the application is executed in a single-threaded
               manner and that you will not get overlapping/concurrent executions
        '''

        proc_entity_obj = ProcedureEntityTag.make(ProcedureManager.next_global_id())
        proc_entity_obj.progress_to_active()
        # After it is constructed, it will progress to queued
        
        self.current_procedure_focus = (proc_entity_obj, stage)
        result = stage.execute(self)

        proc_entity_obj.progress_to_next_state() # Should be marked as completed now

        # Returns a result after the execution is finished
        return result


    @with_debug_log()
    def execute_defer(self, stage: RottnestCompilerStage):
        '''
           Defers the execution to the queue
               Will be executed when time is available 
        '''
        proc_entity_obj = ProcedureEntityTag.make(ProcedureManager.next_global_id())
        proc_entity_obj.progress_to_next_state()
        # After it is constructed, it will progress to queued
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
        entity_obj, proc = self.queued_tasks.get(True, self.queue_timeout)

        if entity_obj:
            entity_id = entity_obj.proc_id
            proc.execute(self)

            self.queued_id_set.discard(entity_id)
            self.queued_tasks.task_done()

            # Entity object will be marked as completed here
            entity_obj.progress_to_next_state()

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

    def get_procedure_state(self, procedure_id: int):
        '''
           Gets the procedure state and checks the relevant buckets to see if
           it exists
               - Likely to check the queued than active
               - If completed is tracked - checks completed otherwise None 
               - Active if not in queued
        '''
        prc_tuple = self.current_procedure_focus
        result = ProcedureEntityStateTag.INVALID
        
        if procedure_id in self.queued_id_set: #In Queued Set
            result = ProcedureEntityStateTag.QUEUED
        elif procedure_id in self.completed_tasks: #In Completed Set
            result = ProcedureEntityStateTag.COMPLETED

        elif prc_tuple is not None:
            prc_entity_obj, proc = self.current_procedure_focus

            if prc_entity_obj.proc_id == procedure_id:
                result = ProcedureEntityStateTag.ACTIVE
                
        return result

    @with_debug_log()
    def get_queued_procedure_ids(self):
        '''
           Retrieves a list of the current enqueued procedures
            - Note: Was originally going to be computed but we keep a dict
                for keeping track of them now

            Do Note: This is likely to just be 1 entry but could be many if
                it gets capability to execute more than 1 at a time.
        '''
        return list(self.queued_id_set)

    @with_debug_log()
    def enqueue_procedure(self, stage):
        '''
           Enqueues the procedure with a global id associated
           - This is a tuple 
        '''
        stage_id = ProcedureManager.next_global_id()
        id_stage_tuple = (stage_id, stage)
        self.queued_id_set.add(stage_id)
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

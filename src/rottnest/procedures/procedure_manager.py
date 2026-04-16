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

    @with_debug_log()
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

    @with_debug_log()
    def progress_to_active(self):
        '''
           For immediate execution mode, it will just jump from constructed to
           active 
        '''
        self.state_tag = ProcedureEntityStateTag.ACTIVE

    @with_debug_log()
    def set_state(self, state_tag: ProcedureEntityStateTag):
        '''
            Sets the current state tag for the execution
        '''
        self.state_tag = state_tag





class ProcedureTuple:
    '''
       Tuple that will hold onto a state object for the
       the procedure as well as provide an intermediary callback
       and finaliser callback for the structure. 
    '''
    def __init__(self, entity_obj: ProcedureEntityStateTag, procedure: RottnestCompilerStage, state_obj=dict(),
                 poll_callback=None, finaliser_callback=None):
        '''
           Initialises the procedure tuple as a way to handle
           the operations right now 
        '''
        self.entity_object = entity_obj
        self.procedure = procedure
        self.procedure_state = state_obj
        self.poll_callback = poll_callback
        self.finaliser_callback = finaliser_callback

    def get_entity_object(self):
        '''
           Gets the entity object that is used for tracking 
        '''
        return self.entity_object


    def get_procedure(self):
        '''
           Gets the procedure from the tuple 
        '''
        return self.procedure

    def get_procedure_state_object(self):
        '''
           Gets the state object, useful for the poll and finaliser calls 
        '''
        return self.procedure_state

    def get_poll_callback(self):
        '''
           Callback that can be injected on poll that uses the state object 
        '''
        return self.poll_callback

    def get_finaliser_callback(self):
        '''
           Callback for when the procedure has completed, used with the
           state object
        '''
        return self.finaliser_callback




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
        self.queued_tasks: queue.Queue[ProcedureTuple] = queue.Queue()

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
        self.current_background_procedure: ProcedureTuple | None = None

        # NOTE: Swithcing over to a procedure manage
        # that has many background tasks running
        self.active_procedures = list()
        self.dispose_procedures_buffer = list()

    @with_debug_log()
    def get_enqueued_size(self) -> int:
        '''
            Gets the number of elements currently enqueued
            within the procedure manager
        '''
        return len(self.queued_id_set)
      
    @classmethod
    @with_debug_log()
    def get_instance(cls, concurrent=True) -> type['ProcedureManager']:
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

            proc_manager = ProcedureManager(app)
            ProcedureManager._manager = proc_manager
            ProcedureManager._manager.app_instance_is_uninit = is_uninit
            # if concurrent:
            #     proc_manager.start_concurrent_manager_in_thread()
            # else:
            proc_manager.start_manager_in_thread()
            
        return ProcedureManager._manager

    @with_debug_log()
    def execute_immediate(self, stage: RottnestCompilerStage, inject_manager=False):
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

        # TODO: Fix up as to not need to inject manager here
        # result = None
        # if inject_manager:
        #     result = stage.execute(self)
        # else:
        result = stage.execute(self)

        proc_entity_obj.progress_to_next_state() # Should be marked as completed now

        # Returns a result after the execution is finished
        return result


    @with_debug_log()
    def complete():
        '''
          To implement required methods for a Stage  
        '''
        return False

    @with_debug_log()
    def execute_defer(self, stage: RottnestCompilerStage, poll_callback=None, finaliser_callback=None, state_obj=dict()):
        '''
           Defers the execution to the queue
               Will be executed when time is available 
        '''
        proc_entity_obj = ProcedureEntityTag.make(ProcedureManager.next_global_id())
        proc_entity_obj.progress_to_next_state()

        procedure_tuple = ProcedureTuple(proc_entity_obj, stage, state_obj, poll_callback, finaliser_callback)
        # After it is constructed, it will progress to queued
        self.enqueue_procedure_tuple(procedure_tuple)
        return True


    @with_debug_log()
    def stop_manager(self):
        '''
           Sets the `should_stop` field to True 
        '''
        self.should_stop = True
    
    @with_debug_log()
    def start_concurrent_manager_in_thread(self) -> Thread:
        '''
            Will create a thread and invoke a start_loop
            for it to run until the meant to finish,
            it will maintain an active list and a dispose
            list of procedures it is working and needs to discard
        '''
        def _thread_worker():
            self.start_loop_concurrent()
            
        thread_joinhandler = Thread(target=_thread_worker, daemon=True)
        thread_joinhandler.start()
        return thread_joinhandler


    
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
    def concurrent_dequeue_and_execute(self, timeout=None):
        '''
           Concurrent execution on active list
           for the procedures given 
        '''
        proc_tuple = None
        
        if timeout is None:
            proc_tuple = self.queued_tasks.get(True, timeout)
        else:
            proc_tuple = self.queued_tasks.get(False)

        # proc_tuple is getting the entry from the queued_tasks
        if proc_tuple is not None:
            self.active_procedures.append(proc_tuple)

        self.concurrent_execute_active_list()


    @with_debug_log()
    def concurrent_execute_active_list(self):
        '''
            It will iterate over the active list
            and provide some time for each procedure by calling
            poll
        '''

        active_list = self.active_procedures
        dispose_list = self.dispose_procedures_buffer
        # Process all procedures
        # Dispose list will be repopulated
        for active_proc_idx in range(len(active_list)):
            self.concurrent_execute_on_procedure(active_proc_idx)

        # Dispose any completed procedures
        # Drains the dispose list - Will be empty for next iteration
        while len(dispose_list) > 0:
            dispose_idx = dispose_list.pop()
            active_list.pop(dispose_idx)


    @with_debug_log()
    def concurrent_execute_on_procedure(self, proc_index):
        '''
           Given a procedure, it will operate on it
           from the active list 
        '''
        proc_tuple = self.active_procedures[proc_index]
        entity_obj = proc_tuple.get_entity_object()
        entity_id = entity_obj.proc_id

        procedure_state = proc_tuple.get_procedure_state_object()
        proc_final_callback = proc_tuple.get_finaliser_callback()

        procedure = proc_tuple.get_procedure()
        if procedure.complete():
            procedure_state.progress_to_next_state()
            self.queued_id_set.discard(entity_id)
            self.dispose_procedures_buffer.append(proc_index)
            if proc_final_callback is not None:
                proc_final_callback(procedure_state)
        else:
            procedure.poll()
            

    @with_debug_log()
    def dequeue_and_execute(self):
        '''
            Dequeue a procedure and execute it by also providing the
            manager as context
        '''
        proc_tuple = self.queued_tasks.get(True, self.queue_timeout)
        if proc_tuple:
            entity_obj = proc_tuple.get_entity_object()
            entity_id = entity_obj.proc_id

            procedure_state = proc_tuple.get_procedure_state_object()
            proc_final_callback = proc_tuple.get_finaliser_callback()

            procedure = proc_tuple.get_procedure()

            # Sets the current defer procedure 
            self.current_background_procedure = proc_tuple
            procedure.execute(self)

            # NOTE: This will check to see if it is complete or not
            while not self.is_background_procedure_complete():
                self.poll_background_procedure()

            self.queued_id_set.discard(entity_id)
            self.queued_tasks.task_done()

            # Entity object will be marked as completed here
            entity_obj.progress_to_next_state()

            # NOTE: Once it is completed, it will need to process the last bit of data
            if proc_final_callback is not None:
                proc_final_callback(procedure_state)

            self.current_background_procedure = None
            

    @with_debug_log()
    def poll_background_procedure(self):
        '''
            Polls the current_background_procedure
        '''
        background_proc_tup = self.current_background_procedure
        if background_proc_tup is not None:
            proc_state = background_proc_tup.get_procedure_state_object()
            poll_callback = background_proc_tup.get_poll_callback()

            # If not assigned, it will ignore it
            if poll_callback is not None:
                poll_callback(proc_state)
            

    @with_debug_log()
    def is_background_procedure_complete(self):
        '''
           Checks to see if the background procedure is finished
           or not 
        '''
        background_proc_tup = self.current_background_procedure
        if background_proc_tup is not None:
            background_proc = background_proc_tup.get_procedure()
            if background_proc is not None:
                return background_proc.complete()
        
        return False
    
    @with_debug_log()
    def start_loop(self):
        '''
           Starts te event loop, will await for tasks to be
           sent by producers and consumed by the manager
               - These are async procedures
        '''
        while not self.should_stop:
            # Blocks until N seconds and throws an exception
            # or has data available
            try:
                self.dequeue_and_execute()
            except queue.Empty:
                # Is to be ignored
                pass

    @with_debug_log()
    def start_loop_concurrent(self):
        '''
           Starts te event loop, will await for tasks to be
           sent by producers and consumed by the manager
               - These are async procedures
        '''
        while not self.should_stop:
            # Blocks until N seconds and throws an exception
            # or has data available
            try:
                if len(self.active_procedures) > 0:
                    # active procedures, only grab what you can
                    self.concurrent_dequeue_and_execute()
                else:
                    # No active processes, wait until procedures are added
                    self.concurrent_dequeue_and_execute(timeout=self.queue_timeout)
            except queue.Empty:
                # Is to be ignored
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
    def enqueue_procedure_tuple(self, procedure_tuple):
        '''
           Enqueues the procedure with a global id associated
           - This is a tuple 
        '''
        self.queued_id_set.add(procedure_tuple.get_entity_object().proc_id)
        self.queued_tasks.put(procedure_tuple)
        

    
    @classmethod
    @with_debug_log()
    def next_global_id(cls):
        '''
           Generates the next integer id - Class level object
        '''
        current = ProcedureManager.NEXT_ID
        ProcedureManager.NEXT_ID += 1
        return current

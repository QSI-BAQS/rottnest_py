from .procedure_tuple import ProcedureTuple, ProcedureEntityStateTag
from .procedure_manager import ProcedureElement, ProcedureManager, ProcedureManagerTimeout
from ..procedure import RottnestCompilerProcedure
import queue

    

class SerialProcedureManager(ProcedureManager):
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

    def __init__(self, app: object, queue_timeout=ProcedureManagerTimeout):
        '''
           Initialising the procedure manager
        '''

        self.queued_id_set: set[int] = set()
        self.queue_timeout = queue_timeout
        self.queued_tasks: queue.Queue[ProcedureTuple] = queue.Queue()
        # Used to provide information regarding the current active procedure
        self.current_procedure_focus: ProcedureElement | None = None

        # NOTE: Switching over to a procedure manage
        # that has many background tasks running
        self.active_procedures = list()
        self.dispose_procedures_buffer = list()

        super().__init__(app)

    

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
        # elif procedure_id in self.completed_tasks: #In Completed Set
            # result = ProcedureEntityStateTag.COMPLETED

        elif prc_tuple is not None:
            prc_entity_obj, proc = prc_tuple
            if prc_entity_obj.proc_id == procedure_id:
                result = ProcedureEntityStateTag.ACTIVE
                
        return result

    # Specialised Serial methods

    def dequeue_and_execute(self):
        '''
            Dequeue a procedure and execute it by also providing the
            manager as context
        '''
        try:
            proc_tuple = self.queued_tasks.get(True, self.queue_timeout)

            if proc_tuple:
                entity_obj = proc_tuple.get_entity_tag()
                entity_id = entity_obj.get_procedure_id()

                procedure_state = proc_tuple.get_procedure_state_object()
                proc_final_callback = proc_tuple.get_finaliser_callback()

                # NOTE: Sets the current defer procedure 
                self.current_background_procedure = proc_tuple
                proc_tuple.execute()

                # NOTE: This will check to see if it is complete or not
                while not self.is_background_procedure_complete():
                    self.poll_background_procedure()

                self.queued_id_set.discard(entity_id)
                self.queued_tasks.task_done()

                # NOTE: Entity object will be marked as completed here
                entity_obj.progress_to_next_state()

                # NOTE: Once it is completed, it will need to
                # process the last bit of data
                if proc_final_callback is not None:
                    proc_final_callback(procedure_state)

                self.current_background_procedure = None
        except queue.Empty:
            pass

    def poll_background_procedure(self):
        '''
            Polls the current_background_procedure
        '''
        background_proc_tup = self.current_background_procedure
        if background_proc_tup is not None:
            procedure = background_proc_tup.get_procedure()
            proc_state = background_proc_tup.get_procedure_state_object()
            poll_wrapper_callback = background_proc_tup.get_poll_callback()

            # If not assigned, it will ignore it
            if poll_wrapper_callback is not None:
                poll_wrapper_callback(proc_state)
            else:
                procedure.poll()
            

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
    
                
    def dispatch(self,
                    proc: RottnestCompilerProcedure,
                    poll_callback=None,
                    complete_callback=None,
                    finaliser_callback=None,
                    procedure_state_obj=dict()) -> bool:
                      
        '''
           Defers the execution to the queue
               Will be executed when time is available 
        '''
        procedure_tuple = ProcedureTuple.with_tagger(
                                self,
                                proc,
                                procedure_state_obj,
                                poll_callback,
                                complete_callback,
                                finaliser_callback)

        # After it is constructed, it will progress to queued
        self.enqueue_procedure_tuple(procedure_tuple)
        return True

    def enqueue_procedure_tuple(self, procedure_tuple):
        '''
           Enqueues the procedure with a global id associated
           - This is a tuple 
        '''
        self.queued_id_set.add(procedure_tuple.get_entity_object().proc_id)
        self.queued_tasks.put(procedure_tuple)


    def run_manager(self):
        '''
           Starts te event loop, will await for tasks to be
           sent by producers and consumed by the manager
               - These are async procedures
        '''
        while not self.soft_stop:
            # Blocks until N seconds and throws an exception
            # or has data available
            try:
                self.dequeue_and_execute()
            except queue.Empty:
                # Is to be ignored
                pass
            

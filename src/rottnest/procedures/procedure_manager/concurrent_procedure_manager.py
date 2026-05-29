from .procedure_tuple import ProcedureTuple
from .procedure_manager import ProcedureManager
from ..procedure import RottnestCompilerProcedure
import queue

class ConcurrentProcedureManager(ProcedureManager):
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


    def __init__(self, app: object = None, queue_timeout=3):
        '''
           Initialises the manager
               * app - access to the application which has
                   access to the websockets that can be used
               * completed_tasks - list of tasks that have been
                   completed. Not used by default
        '''
        self.queued_id_set: set[int] = set()
        self.queue_timeout = queue_timeout
        self.queued_tasks: queue.Queue[ProcedureTuple] = queue.Queue()

        self.active_procedures: list[ProcedureTuple] = list()
        self.dispose_procedures_buffer: list[int] = list()
        super().__init__(app)


<<<<<<< HEAD
    def dispatch(
                self,
                proc: RottnestCompilerProcedure,
                poll_callback=None,
                complete_callback=None,
                finaliser_callback=None,
                procedure_state_obj=None) -> bool:
=======
    def dispatch(self,
                    proc: RottnestCompilerProcedure,
                    poll_callback=None,
                    complete_callback=None,
                    finaliser_callback=None,
                    procedure_state_obj=dict()) -> bool:
>>>>>>> 0de0c85254dbc876525db903237ec8693fa09a07
                      
        '''
           Defers the execution to the queue
               Will be executed when time is available 
        '''
<<<<<<< HEAD
        if procedure_state_obj is None:
            procedure_state_obj = dict()

=======
>>>>>>> 0de0c85254dbc876525db903237ec8693fa09a07
        procedure_tuple = ProcedureTuple.with_tagger(
                                self,
                                proc,
                                procedure_state_obj,
                                poll_callback,
                                complete_callback,
                                finaliser_callback)

        # After it is constructed, it will progress to queued
        self._concurrent_enqueue_procedure_tuple(procedure_tuple)
        return True

    def get_procedure(self, procedure_id: int) -> ProcedureTuple | None:
        '''
           Gets the procedure state and checks the relevant buckets to see if
           it exists
               - Likely to check the queued than active
               - If completed is tracked - checks completed otherwise None 
               - Active if not in queued
        '''
        result = None
        for proc in self.active_procedures:
            if proc.get_procedure_id() == procedure_id:
                result = proc
                break
        
        return result

    def get_enqueued_size(self) -> int:
        '''
            Gets the number of elements currently enqueued
            within the procedure manager
        '''
        return len(self.queued_id_set)


    def run_manager(self):
        '''
           Starts te event loop, will await for tasks to be
           sent by producers and consumed by the manager
               - These are async procedures
        '''
        while not self.hard_stop:
            # Blocks until N seconds and throws an exception
            # or has data available
            if self.soft_stop:
                # No more procedures will be dequeued
                
                self._concurrent_execute_active_list()
                if self._get_active_list_length() == 0:
                    self.hard_stop = True
            else:
                
                if len(self.active_procedures) > 0:
                    # active procedures, only grab what you can
                    self._concurrent_dequeue_and_execute()
                else:
                    # No active processes, wait until procedures are added
                    self._concurrent_dequeue_and_execute(timeout=self.queue_timeout)
    

    def _get_active_list_length(self):
        '''
           Outlines how many procedures are still currently active 
        '''
        return len(self.active_procedures)


    def _concurrent_dequeue_and_execute(self, timeout=None):
        '''
           Concurrent execution on active list
           for the procedures given 
        '''
        proc_tuple = None
        
        try:
            if timeout is not None:
                proc_tuple = self.queued_tasks.get(True, timeout)
            else:
                proc_tuple = self.queued_tasks.get(False)

            # proc_tuple is getting the entry from the queued_tasks
            if proc_tuple is not None:
                self.queued_tasks.task_done()
                self.active_procedures.append(proc_tuple)
                proc_tuple.execute()
        except queue.Empty:
            pass
                
        self._concurrent_execute_active_list()


    def _concurrent_execute_active_list(self):
        '''
            It will iterate over the active list
            and provide some time for each procedure by calling
            poll
        '''

        active_list = self.active_procedures
        # Process all procedures
        # Dispose list will be repopulated
        for active_proc_idx in range(len(active_list)):
            self._concurrent_execute_on_procedure(active_proc_idx)

        self._cleanup_active_list()

    def _cleanup_active_list(self):
        '''
           Any active procedures that have completed will need to be
           disposed of 
        '''
        active_list = self.active_procedures
        dispose_list = self.dispose_procedures_buffer
        # Dispose any completed procedures
        # Drains the dispose list - Will be empty for next iteration
        while len(dispose_list) > 0:
            dispose_idx = dispose_list.pop()
            active_list.pop(dispose_idx)


    def _concurrent_execute_on_procedure(self, proc_index):
        '''
           Given a procedure, it will operate on it
           from the active list
        '''
        proc_tuple: ProcedureTuple = self.active_procedures[proc_index]
        entity_obj = proc_tuple.get_entity_tag()
        procedure_state = proc_tuple.get_procedure_state_object()
        proc_final_callback = proc_tuple.get_finaliser_callback()

        procedure_wrapper_complete = proc_tuple.get_complete_callback_or_default()
        procedure_wrapper_poll = proc_tuple.get_poll_callback()
        procedure = proc_tuple.get_procedure()

        
        if procedure_wrapper_complete(procedure_state):
            entity_obj.progress_to_next_state()
            self.queued_id_set.remove(entity_obj.proc_id)
            self.dispose_procedures_buffer.append(proc_index)
            if proc_final_callback is not None:
                proc_final_callback(procedure_state)
        else:
            if procedure_wrapper_poll is not None:
                procedure_wrapper_poll(procedure_state)
            else:
                procedure.poll()

    def _concurrent_enqueue_procedure_tuple(self, procedure_tuple):
        '''
           Enqueues the procedure with a global id associated
           - This is a tuple 
        '''
        self.queued_id_set.add(procedure_tuple.get_entity_tag().proc_id)
        self.queued_tasks.put(procedure_tuple)
        
    def get_queued_procedure_ids(self):
        '''
           Retrieves a list of the current enqueued procedures
            - Note: Was originally going to be computed but we keep a dict
                for keeping track of them now

            Do Note: This is likely to just be 1 entry but could be many if
                it gets capability to execute more than 1 at a time.
        '''
        return list(self.queued_id_set)
        

    

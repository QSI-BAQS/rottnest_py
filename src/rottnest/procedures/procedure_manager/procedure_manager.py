from enum import Enum
from multiprocessing import Queue
from typing import Protocol
from threading import Thread

from .procedure_tuple import ProcedureEntityTag, ProcedureTuple
from ..procedure import RottnestCompilerProcedure
from ..stage import RottnestCompilerStage

ProcedureElement = tuple[ProcedureEntityTag, ProcedureTuple]
ProcedureManagerTimeout = 3


class ProcedureManagerExit(Enum):
    '''
       Used to indicate how the manager has exited
    '''
    Normal = 0
    SoftExit = 1
    HardExit = 2
    AbornalExit = 3

class AppContextType(Protocol):
    '''
       Protocol of the application context - Typically
           would be RottnestApplication 
    '''

    def try_get_instance(self) -> None | object:
        '''
            Will attempt to get the instance
        '''
        pass

    def get_uninitialised_instance(self) -> object:
        '''
            Will get an instance that is partially initiallised
        '''
        pass

    def get_websocket(self) -> object:
        '''
           Gets the websocket from the context itself 
        '''
        pass


<<<<<<< HEAD
class ProcedureManager:
=======
class ProcedureManager(RottnestCompilerStage):
>>>>>>> 0de0c85254dbc876525db903237ec8693fa09a07
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

    NEXT_ID = 1
    LAST_ISSUED_ID: int | None = None

    def __init__(self, app: object | None = None):
        '''
            Initialises the instance itself which will also maintain
            the current ids here

            app context - Gets the application it is working on
            thread_handle - is a hook for when a thead is used, otherwise None
            has_stopped - Outlines that the procedure manager has stopped
            soft_stop - Will stop accepting new jobs and complete the remaining
            hard_stop - Will stop on next manager_tick
        '''
        self.context = app
        self.thread_handle = None
        self.has_stopped = False
        self.soft_stop = False
        self.hard_stop = False


    @classmethod
    def next_global_id(cls):
        '''
           Generates the next integer id - Class level object
        '''
        current = ProcedureManager.NEXT_ID
        ProcedureManager.LAST_ISSUED_ID = current
        ProcedureManager.NEXT_ID += 1
        return current
    
    @classmethod
    def last_issued_global_id(cls):
        '''
           Generates the next integer id - Class level object
        '''
        return ProcedureManager.LAST_ISSUED_ID

    def get_next_id(self) -> int:
        '''
            Instance wrapper around the `next_global_id` call
        '''
        return ProcedureManager.next_global_id()

    def get_context(self, ctx_type: AppContextType) -> object | None:
        '''
            Gets the rottnest application data that it has
            attached, this will icnlude websockets and plugins

            This is a safe wrapped for checking to see if
            application is now initialised
        '''
        retapp = self.context
        if retapp is None:
            retapp = ctx_type.try_get_instance()
            self.context = retapp

        return retapp

    def get_current_id(self) -> int | None:
        '''
            Gets the current id for the entity
        '''
        return self.LAST_ISSUED_ID

    def tag_procedure(self, proc: RottnestCompilerProcedure):
        '''
           Tags the procedure with an id that will be used 
        '''
        proc_entity_obj = ProcedureEntityTag.make(self.get_next_id())
        proc_entity_obj.progress_to_next_state()
        

    def get_procedure_state_from_id(self, procedure_id: int) -> ProcedureTuple:
        '''
           Gets the procedure state and checks the relevant buckets to see if
           it exists
               - Likely to check the queued than active
               - If completed is tracked - checks completed otherwise None 
               - Active if not in queued
        '''
        raise NotImplementedError

    def get_procedure_table(self) -> list[ProcedureTuple]:
        '''
            Returns the procedure table related to the
            current active procedures
        '''
        raise NotImplementedError

    def get_manager_queue_length(self) -> int:
        '''
            Gets the number of elements currently enqueued
            within the procedure manager
        '''
        raise NotImplementedError
    
    def get_manager_queue(self) -> Queue:
        '''
            Gets the queue in which procedures are stored
        '''
        raise NotImplementedError
        
    def dispatch(self,
                    proc: RottnestCompilerProcedure,
                    poll_callback=None,
                    complete_callback=None,
                    finaliser_callback=None,
                    procedure_state_obj=dict()) -> bool:
                      
        '''
            Will use dispatch immediate but should be overriden to
            implement a specialised scheme
        '''
        return self.dispatch_immediate(proc)
        
    def dispatch_immediate(self, proc: RottnestCompilerProcedure):
        '''
           Executes the procedure immediately
           Return any data from the stage

           NOTE: It is assumed that the application is executed in a single-threaded
               manner and that you will not get overlapping/concurrent executions
               unless you are using the concurrent procedure manager
        '''
        proc_entity_obj = ProcedureEntityTag.make(ProcedureManager.next_global_id())
        proc_tuple = ProcedureTuple(proc_entity_obj, proc)
        proc_entity_obj.progress_to_active()
        
        result = proc_tuple.execute()

        proc_entity_obj.progress_to_next_state()
        return result
    
    def stop_manager(self):
        '''
            Set a soft stop for the manager
            Will complete remaining jobs before quitting
        '''
        self.soft_stop = True
    
    def terminate_manager(self):
        '''
           Sets a hard stop for the manager 
        '''
        self.hard_stop = True
        
    def get_manager_thread_handle(self):
        '''
           Gets a handle of the thread that holds a reference
           of the object 
        '''
        return self.thread_handle

    def start_manager_in_thread(self):
        '''
           Starts the manager in a thread and returns its thread handle 
        '''
        def _thread_worker():
            self.run_manager()
            
        thread_joinhandler = Thread(target=_thread_worker, daemon=True)
        thread_joinhandler.start()
        self.thread_handle = thread_joinhandler
        return thread_joinhandler

    
    def run_manager(self) -> ProcedureManagerExit:
        '''
            Outlines the loop in which the manager operates in
        '''
        raise NotImplementedError

    def execute(self,
            compiler_environment = None,
            reporting=True,
            single_pass=False) -> bool | None:
        '''
           Reimplements the execute method for Procedure
           Calls itself by running 'run_manager'
        '''

        self.run_manager()
        
        

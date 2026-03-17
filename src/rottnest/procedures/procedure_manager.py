from rottnest.procedures.stage import RottnestCompilerStage
from rottnest.server.app.application import RottnestApplication
from rottnest.debug.util import with_debug_log
from threading import Thread
import queue


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

    # Singleton Instance
    _manager = None

    @with_debug_log()
    def __init__(self, app: RottnestApplication, \
                 track_stage_completion=False):
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
        
        self.track_stage_completion = track_stage_completion
        self.queue_timeout = 10
        self.queued_tasks: queue.Queue[RottnestCompilerStage] = queue.Queue()
        self.completed_tasks = list()
        self.should_stop = False

    
    @classmethod
    def get_instance():
        '''
           Singleton object that can be retrieved
           by the procedures

           _manager is the singleton instance here
        '''
        if ProcedureManager._manager is None:
            app = RottnestApplication.get_instance()
            ProcedureManager._manager = ProcedureManager(app)
        else:
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
        self.queued_tasks.put(stage)
        return True


    @with_debug_log()
    def stop_manager(self):
        '''
           Sets the `should_stop` field to True 
        '''
        self.should_stop = True
    
    @with_debug_log()
    def start_manager_in_thread(self):
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
                proc = self.queued_tasks.get(True, self.queue_timeout)
                proc.execute(self)
                self.queued_tasks.task_done()
            except queue.Empty:
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
        


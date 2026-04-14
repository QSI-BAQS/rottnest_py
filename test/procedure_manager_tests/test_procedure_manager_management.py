from io import StringIO
from geventwebsocket.websocket import WebSocket
from threading import Semaphore
from rottnest.procedures.procedure_manager import ProcedureManager
from rottnest.server.app.application import RottnestApplication
import unittest
import time

from rottnest.procedures import procedure, stage, exceptions

class ProcedureInspectionTools:
    '''
       Inspection tools here allow for generating indices/ids to
       track what procedure has been executed and what is in a queue

       This allows for ensuring a deterministic bit of machinery
       when the manager is active 
    '''

    NEXT_INTEGER = 1

    @classmethod
    def generate_next_id(cls):
        '''
           Generates the next integer 
        '''
        current = ProcedureInspectionTools.NEXT_INTEGER
        ProcedureInspectionTools.NEXT_INTEGER += 1
        return current


class ProcedureExample(stage.RottnestCompilerStage):
    '''
       Used as a mechanism to test within the management
       Provides some introspection mechanisms.
    '''
    TAG = 'ProcedureExample'

    def __init__(self, *, tag=None, dependencies=None):
        '''
           This example variant does not contain any dependencies
           But we maintain a state variable to indicuate if it has been
           executed and an index of it 
        '''

        self.proc_id = ProcedureInspectionTools.generate_next_id()
        self.executed = False

    @classmethod
    def Make(cls):
        '''
           Factory method that creates a new procedure example 
        '''
        return ProcedureExample()

    def execute(self, compiler_environment):
        '''
            Executes the procedure 
        '''
        self.executed = True

    def get_tag(self):
        '''
           Gets the tag of the procedure example object 
        '''
        strfmt = f"{self.__class__.__name__}:{self.proc_id}:{self.executed}"
        return strfmt

class ProcedureManagerManagementTest(unittest.TestCase):
    '''
       Management aspect ehre is to ensure that the procedure manager
       is able to mdoified and mediated by another actor within
       the rottnest system 
    '''

    def test_launch_in_thread_and_sleep_quit(self):
        '''
           Launch and Sleep will run the manager and then
           ensure that it can be stopped and disposed of 
        '''

        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())
        thread_handler = procman.start_manager_in_thread()

        time.sleep(2)

        procman.stop_manager() # NOTE: Should set it as FALSE and stop it
            # may be delayed though

        thread_handler.join()


    def test_get_instance_without_init(self):
        '''
           Be able to retrieve the instance without needing to initialise
           the manager explicitly 
        '''
        procman = ProcedureManager.get_instance()
        assert procman is not None
        

    def test_execute_defer_single(self):
        '''
            Is able to enqueue but defer the execute with existing procedures
            Only a single procedure is required, count should be reflected
            accurately    
        '''
        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())

        # Use test procedure included in class
        procman.execute_defer(ProcedureExample.Make())
        assert procman.get_enqueued_size() == 1

    def test_execute_defer_many(self):
        '''
            Is able to enqueue but defer the execute with existing procedures
            Only a single procedure is required, count should be reflected
            accurately    
        '''
        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())

        # Use test procedure included in class
        procman.execute_defer(ProcedureExample.Make())
        procman.execute_defer(ProcedureExample.Make())
        procman.execute_defer(ProcedureExample.Make())
        procman.execute_defer(ProcedureExample.Make())

        assert procman.get_enqueued_size() == 4
        
    def test_app_instance_state_uninit_to_init(self):
        '''
            This should check to see if the procedure manager is able
            to handle a situation where the instance given is initially uninit'd
            then transforms

            - Refers to `get_rottnest_application`
        '''

        app_uninit = RottnestApplication.get_uninitialised_instance()
        procman = ProcedureManager(app_uninit)

        mock_wsock = WebSocket(None, StringIO(''), None) # NOTE: Un-init'd
        mock_wsock_sem = Semaphore()

        # Gets to see if the application is the same as the uninit version
        assert procman.get_rottnest_application() is app_uninit

        # After the next line, this should be initialised
        rottapp = RottnestApplication(mock_wsock, mock_wsock_sem)

        # Checks to see if it is now the initialised version
        assert procman.get_rottnest_application() is rottapp
        
        

if __name__ == '__main__':

    # Runs all the test cases
    unittest.main()

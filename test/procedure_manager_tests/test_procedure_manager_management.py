from rottnest.procedures.procedure_manager.procedure_manager_selector import ProcedureManagerSelector
import unittest
import time

from rottnest.procedures import stage

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
        super().__init__(tag=ProcedureExample.TAG,
                         dependencies=[], asynchronous=True)

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

        

class ProcedureManagerManagementTest(unittest.TestCase):
    '''
       Management aspect here is to ensure that the procedure manager
       is able to mdoified and mediated by another actor within
       the rottnest system 
    '''

    def test_launch_in_thread_and_sleep_quit(self):
        '''
           Launch and Sleep will run the manager and then
           ensure that it can be stopped and disposed of 
        '''

        procman = ProcedureManagerSelector.get_default_procedure_manager()

        time.sleep(2)

        procman.stop_manager() # NOTE: Should set it as FALSE and stop it
        # may be delayed though


    def test_get_instance_without_init(self):
        '''
           Be able to retrieve the instance without needing to initialise
           the manager explicitly 
        '''
        procman = ProcedureManagerSelector.get_default_procedure_manager()
        procman.stop_manager() # NOTE: Should set it as FALSE and stop it
        assert procman is not None
        


    def test_execute_defer_many(self):
        '''
            Is able to enqueue but defer the execute with existing procedures
            Only a single procedure is required, count should be reflected
            accurately    
        '''

        procman = ProcedureManagerSelector.get_default_procedure_manager()
        # Use test procedure included in class
        procman.dispatch(ProcedureExample.Make())
        procman.dispatch(ProcedureExample.Make())
        procman.dispatch(ProcedureExample.Make())
        procman.dispatch(ProcedureExample.Make())

        procman.stop_manager() # NOTE: Should set it as FALSE and stop it
        assert procman.get_enqueued_size() == 4
        
        
        

if __name__ == '__main__':

    # Runs all the test cases
    unittest.main()

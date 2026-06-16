from rottnest.process_pool.singleton import get_pool
from rottnest.test_utils.executable import SampleExecutable
from rottnest_preprocessor.preprocessor.architecture import PreprocessorArchitecture
import rottnest.test_utils
from rottnest.plugins import architectures, executables
import rottnest.procedures.preprocess_and_execute
from rottnest.procedures.procedure_manager.procedure_manager_selector import ProcedureManagerSelector
import unittest
import time
        
class ProcedureManagerPreprocExecuteTest(unittest.TestCase):
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

        executables.load_modules_from_strings(rottnest.test_utils.__file__)
        executables.set_current_executable(
            SampleExecutable.get_name() 
        )

        architectures.set_current_architecture(PreprocessorArchitecture.get_name())

        procedure = rottnest.procedures.preprocess_and_execute.PreprocAndExecuteProcedure(reporting=False)

        procman.dispatch(procedure)
        
        time.sleep(2)


        while not procedure.complete():
            procedure.poll()

        assert procedure.preprocessor.get_rz_count() == 1680 
        assert procedure.preprocessor.set_rz_precision() == 20 
        assert procedure.preprocessor.get_t_count() == 1680
        
        procman.stop_manager() # NOTE: Should set it as FALSE and stop it
        # may be delayed though

        self.term()



        

    def term(self):
        pool = get_pool()
        pool.terminate()

        
        

if __name__ == '__main__':
    t = ProcedureManagerPreprocExecuteTest()
    t.test_launch_in_thread_and_sleep_quit()
    

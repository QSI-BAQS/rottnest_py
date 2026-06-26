from rottnest.procedures.preprocess_and_execute.procedure_preprocess_and_execute import PreprocAndExecuteProcedure
from rottnest.process_pool.singleton import get_pool
from rottnest.plugins import architectures, executables
from rottnest.procedures.procedure_manager.procedure_manager_selector import ProcedureManagerSelector
from rottnest.compute_units.layout_proxy import LayoutProxy
from t_scheduler.region_builder.json_to_region import json_to_layout, example as layout 
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

        target_module_string = 'Four Stage Superconducting' 
        target_executable = 'Fermi-Hubbard'
        params = {'N':2}

        # Setup the pool
        architectures.set_current_architecture(
            target_module_string    
        )
        # layout_id = 0
        LayoutProxy.add_layout(layout)

        # Saves architecture for preprocessor
        executables.set_current_executable(
            target_executable 
        )
        executables.set_executable_params(**params)

        procedure = PreprocAndExecuteProcedure()
        # stages = procedure._stages
        procman.dispatch(procedure)


        procman.stop_manager()

        while not procman.stopped():
            time.sleep(2)
        

        # assert procedure.preprocessor.get_rz_count() == 1680 
        # assert procedure.preprocessor.set_rz_precision() == 20 
        # assert procedure.preprocessor.get_t_count() == 1680
        # NOTE: Use to assert preprocessor but just does a runthrough
        
        # may be delayed though

        self.term()
        

    def term(self):
        pool = get_pool()
        pool.terminate()

        
        

if __name__ == '__main__':
    t = ProcedureManagerPreprocExecuteTest()
    t.test_launch_in_thread_and_sleep_quit()
    

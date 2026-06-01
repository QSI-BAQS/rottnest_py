from rottnest.procedures.procedure_manager.procedure_manager_selector import ProcedureManagerSelector
import unittest
from rottnest.procedures import stage

import time

DELAY_TO_DO_WORK = 2

# TODO: Refactor this into their own files/modules for simplicity
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
    GENERATED_OBJECTS = []
    TAG = 'ProcedureExample'

    def __init__(self, *, tag=None, dependencies=None):
        '''
           This example variant does not contain any dependencies
           But we maintain a state variable to indicuate if it has been
           executed and an index of it 
        '''

        self.proc_id = ProcedureInspectionTools.generate_next_id()
        self.executed = False
        self._complete = False

    @classmethod
    def Make(cls):
        '''
           Factory method that creates a new procedure example 
        '''
        proc = ProcedureExample()
        ProcedureExample.GENERATED_OBJECTS.append(proc)
        return proc

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

    def poll(self):
        self._complete = True

class ProcedureManagerTest(unittest.TestCase):


    def test_single_procedure_immediate(self):
        '''
           A single procedure that is then 
        '''

        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS

        procman = ProcedureManagerSelector.get_default_procedure_manager()
                
        # Use test procedure included in class
        procman.dispatch(ProcedureExample.Make())


        procman.stop_manager()
        
        only_proc = procs_generated_ref[0]
        assert only_proc.executed

    def test_many_procedures_immediate_with_thread(self):
        '''
           Tests processing many procedures to be immediately executed 
        '''        
        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS

        procman = ProcedureManagerSelector.get_default_procedure_manager()

        # Use test procedure included in class
        procman.dispatch(ProcedureExample.Make())
        procman.dispatch(ProcedureExample.Make())
        procman.dispatch(ProcedureExample.Make())
        procman.dispatch(ProcedureExample.Make())

        time.sleep(DELAY_TO_DO_WORK)
        procman.stop_manager()

        for g in procs_generated_ref:
            assert g.executed # NOTE: Since the procedure is controlled
                # we can observe the state of it


    def test_single_procedure_enqueue(self):
        '''
           Single procedure that is enqueued into the procedure manager
           Making sure it gets pushed through in it 
        '''
        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS

        procman = ProcedureManagerSelector.get_default_procedure_manager()


        procman.dispatch(ProcedureExample.Make())
        

        assert procman.get_enqueued_size() == 1


        time.sleep(DELAY_TO_DO_WORK)
        
        procman.stop_manager()
        
        assert procman.get_enqueued_size() == 0


        only_proc = procs_generated_ref[0]
        assert only_proc.executed

if __name__ == '__main__':
    unittest.main()


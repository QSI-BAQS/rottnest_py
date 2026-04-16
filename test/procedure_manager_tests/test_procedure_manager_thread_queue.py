import unittest
from rottnest.procedures.procedure_manager import ProcedureManager
from rottnest.server.app.application import RottnestApplication

from rottnest.procedures import procedure, stage, exceptions

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

class ProcedureManagerTest(unittest.TestCase):


    def test_single_procedure_immediate(self):
        '''
           A single procedure that is then 
        '''

        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS
        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())
        
        # Use test procedure included in class
        procman.execute_immediate(ProcedureExample.Make())

        only_proc = procs_generated_ref[0]
        assert only_proc.executed

    def test_many_procedures_immediate_with_thread(self):
        '''
           Tests processing many procedures to be immediately executed 
        '''        
        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS
        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())

        handler = procman.start_concurrent_manager_in_thread()
        # Use test procedure included in class
        procman.execute_immediate(ProcedureExample.Make())
        procman.execute_immediate(ProcedureExample.Make())
        procman.execute_immediate(ProcedureExample.Make())
        procman.execute_immediate(ProcedureExample.Make())

        procman.stop_manager()
        handler.join()

        for g in procs_generated_ref:
            assert g.executed # NOTE: Since the procedure is controlled
                # we can observe the state of it


    def test_single_procedure_enqueue(self):
        '''
           Single procedure that is enqueued into the procedure manager
           Making sure it gets pushed through in it 
        '''
        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS
        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance(),\
                                   queue_timeout=1)

        handler = procman.start_concurrent_manager_in_thread()
        # procman.start_loop() # Starts working

        # Use test procedure included in class
        procman.execute_defer(ProcedureExample.Make())

        assert procman.get_enqueued_size() == 1
        procman.dequeue_and_execute()
        assert procman.get_enqueued_size() == 0

        procman.stop_manager()
        handler.join()

        only_proc = procs_generated_ref[0]
        assert only_proc.executed

    def test_many_procedure_enqueue_and_execute(self):
        '''
            Aim is to stack a number of procedures and execute them
            in sequence using the defer method and explicit dequeuing
        '''
        procs_generated_ref = ProcedureExample.GENERATED_OBJECTS
        procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())

        handler = procman.start_concurrent_manager_in_thread()

        # Use test procedure included in class
        procman.execute_defer(ProcedureExample.Make())
        procman.execute_defer(ProcedureExample.Make())
        procman.execute_defer(ProcedureExample.Make())
        procman.execute_defer(ProcedureExample.Make())

        assert procman.get_enqueued_size() == 4

        procman.dequeue_and_execute()
        assert procman.get_enqueued_size() == 3
        procman.dequeue_and_execute()
        assert procman.get_enqueued_size() == 2
        procman.dequeue_and_execute()
        assert procman.get_enqueued_size() == 1
        procman.dequeue_and_execute()
        assert procman.get_enqueued_size() == 0

        procman.stop_manager()
        handler.join()

        for g in procs_generated_ref:
            assert g.executed # NOTE: Since the procedure is controlled
                # we can observe the state of it


    # TODO: Throw procedures that have dependencies and codependencies within
    #  the system right now

if __name__ == '__main__':
    unittest.main()


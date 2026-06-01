from rottnest.procedures.procedure_manager.procedure_tuple import ProcedureTuple, ProcedureTagger, ProcedureEntityStateTag, ProcedureEntityTag
from rottnest.procedures import stage
import unittest

DELAY_TO_DO_WORK = 2

# TODO: Refactor this into their own files/modules for simplicity
class ProcedureInspectionTools(ProcedureTagger):
    '''
       Inspection tools here allow for generating indices/ids to
       track what procedure has been executed and what is in a queue

       This allows for ensuring a deterministic bit of machinery
       when the manager is active 
    '''

    NEXT_INTEGER = 1

    @classmethod
    def get_next_id(cls):
        '''
           Generates the next integer 
        '''
        current = ProcedureInspectionTools.NEXT_INTEGER
        ProcedureInspectionTools.NEXT_INTEGER += 1
        return current


    @classmethod
    def get_current_id(cls):
        '''
            Gets the last id 
        '''
        last_id = ProcedureInspectionTools.NEXT_INTEGER
        return last_id

class ProcedureExample(stage.RottnestCompilerStage):
    '''
       Used as a mechanism to test within the management
       Provides some introspection mechanisms.
    '''
    GENERATED_OBJECTS = []
    TAG = 'ProcedureExample'

    def __init__(self, *, tag=None, dependencies=None, entity_id=None):
        '''
           This example variant does not contain any dependencies
           But we maintain a state variable to indicuate if it has been
           executed and an index of it 
        '''
        self.entity_id = entity_id
        self.executed = False
        self._complete = False

    @classmethod
    def Make(cls, tagger=None):
        '''
           Factory method that creates a new procedure example 
        '''
        entity_id = None
        if tagger is not None:
            entity_id = tagger.get_current_id()
        proc = ProcedureExample(entity_id=entity_id)
        ProcedureExample.GENERATED_OBJECTS.append(proc)
        return proc

    def execute(self, compiler_environment):
        '''
            Executes the procedure 
        '''
        self.executed = True

    def poll(self, compiler_environment=None):
        self._complete = True


class ProcedureTupleTestSuite(unittest.TestCase):

    def get_dummy_callbacks(self):

        final_object = [True]
        poll_counter = [0]
        complete = [False]

        def dummy_complete():
            return complete[0]

        def dummy_poll():
            poll_counter[0] += 1
            return poll_counter[0]

        def dummy_finaliser():
            return poll_counter[0], complete[0], final_object[0]

        return (dummy_poll, dummy_complete, dummy_finaliser)


    def test_procedure_tuple_construction_with_entity_id(self):
        insp = ProcedureInspectionTools()
        last_id = insp.get_current_id()
        tup = ProcedureTuple.with_tagger(insp, ProcedureExample.Make(insp))

        assert tup is not None
        assert tup.get_entity_state() == ProcedureEntityStateTag.QUEUED
        assert tup.get_complete_callback() is None
        assert tup.get_entity_tag().get_procedure_id() == last_id
        assert tup.get_finaliser_callback() is None
        assert tup.get_poll_callback() is None
        assert tup.get_procedure() is not None


    def test_procedure_tuple_construction_with_only(self):
        
        insp = ProcedureInspectionTools()
        tup = ProcedureTuple.only(ProcedureEntityTag.make(insp.get_current_id()), ProcedureExample.Make(insp))
        last_id = insp.get_current_id()

        assert tup is not None
        assert tup.get_complete_callback() is None
        assert tup.get_entity_state() == ProcedureEntityStateTag.CONSTRUCTED
        assert tup.get_entity_tag().get_procedure_id() == last_id
        assert tup.get_finaliser_callback() is None
        assert tup.get_poll_callback() is None
        assert tup.get_procedure() is not None

        
    def test_procedure_tuple_construction_with_callbacks_and_executes(self):
        poll_cb, complete_cb, finalise_cb = self.get_dummy_callbacks()
        insp = ProcedureInspectionTools()
        tup = ProcedureTuple.with_tagger(insp, ProcedureExample.Make(insp), poll_callback=poll_cb,
                                         complete_callback=complete_cb, finaliser_callback=finalise_cb,
                                         state_obj=None)

        assert tup is not None
        assert tup.get_complete_callback() is not None
        assert tup.get_poll_callback() is not None
        assert tup.get_finaliser_callback() is not None
        assert tup.get_procedure() is not None

        assert tup.get_poll_callback()() == 1
        assert tup.get_complete_callback()() is False
        assert tup.get_finaliser_callback()()[2] is True
        
        
    def test_procedure_tuple_state_progression_valid(self):

        insp = ProcedureInspectionTools()
        tup = ProcedureTuple.only(ProcedureEntityTag.make(insp.get_current_id()), ProcedureExample.Make(insp))

        entity_tag = tup.get_entity_tag()
        assert entity_tag.progress_to_next_state() == ProcedureEntityStateTag.QUEUED
        assert entity_tag.progress_to_next_state() == ProcedureEntityStateTag.ACTIVE
        assert entity_tag.progress_to_next_state() == ProcedureEntityStateTag.COMPLETED
        
    def test_procedure_tuple_state_progression_jump_to_invalid(self):

        insp = ProcedureInspectionTools()
        tup = ProcedureTuple.only(ProcedureEntityTag.make(insp.get_current_id()), ProcedureExample.Make(insp))

        entity_tag = tup.get_entity_tag()
        assert entity_tag.progress_to_next_state() == ProcedureEntityStateTag.QUEUED
        entity_tag.mark_as_invalid()
        assert entity_tag.get_state_tag() == ProcedureEntityStateTag.INVALID
        
    def test_procedure_tuple_state_progression_jump_to_active(self):

        insp = ProcedureInspectionTools()
        tup = ProcedureTuple.only(ProcedureEntityTag.make(insp.get_current_id()), ProcedureExample.Make(insp))

        entity_tag = tup.get_entity_tag()
        entity_tag.progress_to_active()
        assert entity_tag.get_state_tag() == ProcedureEntityStateTag.ACTIVE


if __name__ == '__main__':
    unittest.main()

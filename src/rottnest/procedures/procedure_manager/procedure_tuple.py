from enum import Enum
from typing import Protocol
from rottnest.procedures.procedure import RottnestCompilerProcedure
from rottnest.procedures.procedure_manager.procedure_state_hook import ProcedureStateHook

class ProcedureTagger(Protocol):
    '''
       Protocol class that requires implementing: 'get_next_id' 
    '''

    def get_next_id(self):
        '''
           Gets the next id 
        '''
        raise NotImplementedError

class ProcedureEntityInvalidState(Exception):
    '''
       In the event the procedure has been considered invalid or aborted
       or something that is not exactly precise, it is worth noting that
       the procedure state should be in an INVALID or ABORTED state 
    '''
    def __init__(self, id):
        super().__init__(f"Attempt to use Invalid Procedure with ID: {id}")


class ProcedureEntityStateTag(Enum):
    '''
       Tag for the execution state
           Allows for clear state transition of the entity being tracked
    '''
    CONSTRUCTED = 1
    QUEUED = 2
    ACTIVE = 3
    COMPLETED = 4
    INVALID = -1

class ProcedureEntityTag:
    '''
       When executing a procedure asynchronously, information about
       the context and what is being executed is worth knowing 
    '''

    def __init__(self, proc_id: int = -1):
        '''
           Initialises the entity tag to be associated with the procedure 
        '''
        self.proc_id = proc_id
        self.state_tag = ProcedureEntityStateTag.CONSTRUCTED

    @classmethod
    def make(cls, proc_id: int) -> 'ProcedureEntityTag':
        '''
           Constructing the procedure with a given procedure id
        '''
        return ProcedureEntityTag(proc_id)

    def get_procedure_id(self):
        '''
           Gets the procedure id that is coupled with the state 
        '''
        return self.proc_id

    def progress_to_next_state(self):
        '''
           Progresses through the states based on the current state it is in
           Only when the state needs to be reset and usually that would result
           in a new procedure being constructed 
        '''
        if self.state_tag == ProcedureEntityStateTag.CONSTRUCTED:
            self.state_tag = ProcedureEntityStateTag.QUEUED
        elif self.state_tag == ProcedureEntityStateTag.QUEUED:
            self.state_tag = ProcedureEntityStateTag.ACTIVE            
        elif self.state_tag == ProcedureEntityStateTag.ACTIVE:
            self.state_tag = ProcedureEntityStateTag.COMPLETED

        # If it is an invalid state
        if self.state_tag == ProcedureEntityStateTag.INVALID:
            raise ProcedureEntityInvalidState(self.proc_id)

    def progress_to_active(self):
        '''
           For immediate execution mode, it will just jump from constructed to
           active 
        '''
        self.state_tag = ProcedureEntityStateTag.ACTIVE

    def get_state_tag(self):
        '''
            Gets the tag of the entity
        '''
        return self.state_tag

    def set_state(self, state_tag: ProcedureEntityStateTag):
        '''
            Sets the current state tag for the execution
        '''
        self.state_tag = state_tag

    def mark_as_invalid(self):
        '''
           Marks the entity as invalid which should ensure that it is discarded
           when labelled in this state 
        '''
        self.state_tag = ProcedureEntityStateTag.INVALID

class ProcedureTuple:
    '''
       Tuple that will hold onto a state object for the
       the procedure as well as provide an intermediary callback
       and finaliser callback for the structure. 
    '''
    def __init__(self, entity_obj: ProcedureEntityTag, \
                 procedure: RottnestCompilerProcedure,
                 state_obj=dict(),
                 poll_callback=None,
                 complete_callback=None,
                 finaliser_callback=None):
        '''
           Initialises the procedure tuple as a way to handle
           the operations right now 
        '''
        self.entity_object = entity_obj
        self.procedure = procedure
        self.procedure_state = state_obj
        self.procedure_hook = ProcedureStateHook(state_obj,
                                        poll_callback,
                                        complete_callback,
                                        finaliser_callback)


    @classmethod
    def with_tagger(cls, tagger: ProcedureTagger,
                    procedure: RottnestCompilerProcedure,
                    poll_callback=None,
                    complete_callback=None,
                    finaliser_callback=None,
                    state_obj=dict()) -> 'ProcedureTuple':
        '''
            Constructs the tuple and generates the id in place 
        '''
        entity_id = tagger.get_next_id()
        proc_entity_tag = ProcedureEntityTag.make(entity_id)
        proc_entity_tag.progress_to_next_state()
        return ProcedureTuple(proc_entity_tag,
                              procedure,
                              poll_callback,
                              complete_callback,
                              finaliser_callback,
                              state_obj)
        

    @classmethod
    def only(cls, entity_id: ProcedureEntityTag,
             procedure: RottnestCompilerProcedure) -> 'ProcedureTuple':
        '''
           Makes it very clear that you are only constructing it with
           an entity id and procedure 
        '''
        return ProcedureTuple(entity_id, procedure)

    def get_entity_state(self) -> ProcedureEntityStateTag:
        '''
           Gets the entity object that is used for tracking 
        '''
        return self.entity_object.get_state_tag()

    def get_entity_tag(self) -> ProcedureEntityTag:
        '''
           Gets the entity tag itself 
        '''
        return self.entity_object

    def get_procedure_id(self) -> int:
        '''
           Gets the procedure id that is associated with the entity 
        '''
        return self.entity_object.get_procedure_id()

    def get_procedure(self):
        '''
           Gets the procedure from the tuple 
        '''
        return self.procedure

    def get_procedure_state_object(self):
        '''
           Gets the state object, useful for the poll and finaliser calls 
        '''
        return self.procedure_state

    def get_poll_callback(self):
        '''
           Callback that can be injected on poll that uses the state object 
        '''
        return self.procedure_hook.get_poll_callback()
    
    def get_complete_callback(self):
        '''
           Callback that can be injected on poll that uses the state object 
        '''
        return self.procedure_hook.get_complete_callback()

    def get_finaliser_callback(self):
        '''
           Callback for when the procedure has completed, used with the
           state object
        '''
        return self.procedure_hook.get_finaliser_callback()

    def execute(self):
        '''
           Executes the procedure that is contained here 
        '''
        self.procedure.execute(self.procedure)

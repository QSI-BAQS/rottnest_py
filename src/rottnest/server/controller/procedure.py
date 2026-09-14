'''
    This interface handles the layout controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.procedure_spec import MODULE_PREFIX, \
    EXECUTE_PROCEDURE_DEFER, GET_PROCEDURES, GET_PROCEDURE_STATE, ABORT_PROCEDURE

from rottnest.server.model import procedure_manager as model 

from rottnest.server.util.result import Result


PROCEDURE_PAYLOAD = 'payload'
PROCEDURE_ID = 'id'

class ProcedureInterface(RouteInterface):
    '''
        Interface for the procedure_manager controllers
        This defines the following operations
            * Launching a procedure based on its tag
            * Getting the status of a procedure based on its id
            * Getting the status of all procedures
            * Aborting a procedure that is currently running
    '''
    # @RouteInterface.bind_route(MODULE_PREFIX, EXECUTE_PROCEDURE_DEFER) 
    # @classmethod
    # def run_procedure_defer(cls, message, **kwargs) -> Result:
    #     '''
    #         Given a procedure key or id, we are able to retrieve the procedure
    #         and submit it to the queue
    #     '''
    #     return Result.Ok(cls.load_and_model_call(
    #         message,
    #         EXECUTE_PROCEDURE_DEFER,
    #         model.procedure_manager_submit_procedure_async                     
    #     ))

    @RouteInterface.bind_route(MODULE_PREFIX, GET_PROCEDURE_STATE) 
    @classmethod
    def get_procedure_state(cls, message, **kwargs) -> Result:
        '''
            Gets the current procedure state of a procedure that is
            completed, queued or active
        '''
        procedure_id = message[PROCEDURE_PAYLOAD][PROCEDURE_ID]
        return Result.Ok(model.get_procedure_state(procedure_id))

    @RouteInterface.bind_route(MODULE_PREFIX, ABORT_PROCEDURE)
    @classmethod
    def get_procedures(cls, message, **kwargs) -> Result:
        '''
            Gets the procedures that are currently active
        '''
        return Result.Ok(model.get_procedure_table())
        
    @RouteInterface.bind_route(MODULE_PREFIX, ABORT_PROCEDURE)
    @classmethod
    def abort_procedure(cls, message, **kwargs) -> Result:
        '''
            Aborts a procedure based on the id that is given
                * If the id matches an existing procedure that the manager
                   is managing, it will trigger an abort
                * If the id does not match, it should outline that
                    that the procedure does not exist 
        '''

        procedure_id = message[PROCEDURE_PAYLOAD][PROCEDURE_ID]
        return Result.Ok(model.abort_procedure(procedure_id))
        
        

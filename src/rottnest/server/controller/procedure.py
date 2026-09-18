'''
    This interface handles the layout controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.procedure_spec import MODULE_PREFIX, \
    EXECUTE_PROCEDURE_DEFER, EXECUTE_PROCEDURE_IMMEDIATE, GET_PROCEDURE_STATE, GET_PROCEDURES, ABORT_PROCEDURE

from rottnest.server.model import procedure_manager as model 

from rottnest.server.util.result import Result

PROCEDURE_PAYLOAD = 'payload'
PROCEDURE_ID = 'procedure_id'

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
   

    @RouteInterface.bind_route(MODULE_PREFIX, GET_PROCEDURE_STATE) 
    @classmethod
    def get_procedure_state(cls, message, **kwargs) -> Result:
        '''
            Gets the current procedure state of a procedure that is
            completed, queued or active
        '''
        procedure_id = message[PROCEDURE_PAYLOAD][PROCEDURE_ID]
        return model.get_procedure_state(procedure_id)

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
    
    @RouteInterface.bind_route(MODULE_PREFIX, GET_PROCEDURES) 
    @classmethod
    def get_procedure_table(cls, message, **kwargs) -> Result:
        '''
            Gets the current procedure state of a procedure that is
            completed, queued or active
        '''
        return Result.Ok(model.procedure_manager_get_active_procedure_list())

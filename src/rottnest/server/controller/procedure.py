'''
    This interface handles the layout controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.procedure_spec import MODULE_PREFIX, \
    EXECUTE_PROCEDURE_DEFER, EXECUTE_PROCEDURE_IMMEDIATE, GET_PROCEDURE_STATE

from rottnest.server.model import procedure_manager as model 

from rottnest.server.util.result import Result


class ProcedureInterface(RouteInterface):
    '''
        Interface for the procedure_manager controllers
    '''
   
    @RouteInterface.bind_route(MODULE_PREFIX, EXECUTE_PROCEDURE_IMMEDIATE) 
    @classmethod
    def run_procedure_immediate(cls, message, **kwargs) -> Result:
        '''
            Skips the queue and uses a procedure key to then
            immediately run it and retrieve the result
        '''
        return Result.Ok(cls.load_and_model_call(
            message,
            EXECUTE_PROCEDURE_IMMEDIATE,
            model.procedure_manager_submit_procedure_sync
        ))

    @RouteInterface.bind_route(MODULE_PREFIX, EXECUTE_PROCEDURE_DEFER) 
    @classmethod
    def run_procedure_defer(cls, message, **kwargs) -> Result:
        '''
            Given a procedure key or id, we are able to retrieve the procedure
            and submit it to the queue
        '''
        return Result.Ok(cls.load_and_model_call(
            message,
            EXECUTE_PROCEDURE_DEFER,
            model.procedure_manager_submit_procedure_async                     
        ))

    @RouteInterface.bind_route(MODULE_PREFIX, GET_PROCEDURE_STATE) 
    @classmethod
    def get_procedure_state(cls, message, **kwargs) -> Result:
        '''
            Gets the current procedure state of a procedure that is
            completed, queued or active
        '''
        return Result.Ok(cls.load_and_model_call(
            message,
            GET_PROCEDURE_STATE,
            model.procedure_manager_get_procedure_state                  
        ))

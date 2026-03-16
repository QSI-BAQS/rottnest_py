'''
    This interface handles the executable controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.executable_spec import (
    MODULE_PREFIX,
    GET_EXECUTABLE_LIST,
    GET_EXECUTABLE_CURRENT,
    SET_EXECUTABLE_CURRENT,
    GET_EXECUTABLE_CONFIG,
    SET_EXECUTABLE_CONFIG 
)

from rottnest.server.model import executable as model 

from rottnest.server.util.result import Result


class ExecutableInterface(RouteInterface):
    '''
        Interface for the executable controllers
    '''
    EXECUTABLE_KEY = 'executable_key'
    EXECUTABLE_CONFIG = 'executable_config'
   
    @RouteInterface.bind_route(MODULE_PREFIX, GET_EXECUTABLE_LIST) 
    @classmethod
    def get_executable_list(cls, message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded executables
            Loads from the singleton instance
        '''
        current, exec_list = model.get_executables()            
        return Result.Ok({
                             "current_executable" : current,
                             "executables": exec_list
                         })
        

    @RouteInterface.bind_route(MODULE_PREFIX, GET_EXECUTABLE_CURRENT) 
    @classmethod
    def get_current_executable(cls, message, **kwargs) -> Result:
        '''
            Gets the currently loaded executable
        '''
        return Result.Ok(model.get_current_executable())

    @RouteInterface.bind_route(MODULE_PREFIX, SET_EXECUTABLE_CURRENT) 
    @classmethod
    def set_current_executable(cls, message, **kwargs) -> Result:
        '''
            Sets the current executable
        '''
        cls.load_and_model_call(
            message,
            cls.EXECUTABLE_KEY,
            model.set_current_executable
        )
        return Result.Ok(model.get_current_executable())

    @RouteInterface.bind_route(MODULE_PREFIX, GET_EXECUTABLE_CONFIG) 
    @classmethod
    def get_current_config(cls, message, **kwargs) -> Result:
        '''
            Gets the configuration options for the 
             current executable
        '''
        return Result.Ok(model.get_current_params())

    @RouteInterface.bind_route(MODULE_PREFIX, SET_EXECUTABLE_CONFIG) 
    @classmethod
    def set_current_config(cls, message, **kwargs) -> Result:
        '''
            Sets the configuration options for the 
             current executable
        '''
        return Result.Ok(cls.load_and_model_call(
            message,
            cls.EXECUTABLE_CONFIG,
            model.set_current_params            
        ))

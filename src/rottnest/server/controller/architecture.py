'''
    This interface handles the architecture controllers
'''

from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.architecture_spec import (
    MODULE_PREFIX,
    GET_ARCHITECTURE_LIST, GET_CURRENT_ARCHITECTURE,
    SET_CURRENT_ARCHITECTURE, GET_ARCHITECTURE_CONFIG,
    SET_ARCHITECTURE_CONFIG)

from rottnest.server.model import plugin_architecture

from rottnest.server.model import architecture as model 
from rottnest.server.responder import Result

class ArchitectureInterface(RouteInterface):
    '''
        Interface for the architecture controllers
    '''

    ARCHITECTURE_KEY = 'architecture_key'
    ARCHITECTURE_CONFIG = 'architecture_config'
    _module_prefix = MODULE_PREFIX
    
    @RouteInterface.bind_route(MODULE_PREFIX, GET_ARCHITECTURE_LIST)
    @classmethod
    def get_architecture_list(cls, message, **kwargs) -> Result:
        '''
            Gets the list of architectures
        '''
        return model.get_architecture_list()

    @RouteInterface.bind_route(MODULE_PREFIX, GET_CURRENT_ARCHITECTURE)
    @classmethod
    def get_current_architecture(cls, message, **kwargs) -> Result:
        '''
           Gets the current architecture 
        '''

    @RouteInterface.bind_route(MODULE_PREFIX, SET_CURRENT_ARCHITECTURE)
    @classmethod
    def set_architecture(cls, message, **kwargs) -> Result:
        '''
           Sets the current architecture
        '''
        return cls.load_and_model_call(
            message,
            cls.EXECUTABLE_KEY,
            model.set_current_executable
        )

    @RouteInterface.bind_route(MODULE_PREFIX, GET_ARCHITECTURE_CONFIG)
    @classmethod
    def get_architecture_config(cls, message, **kwargs) -> Result:
        '''
           Gets an architecture config
        '''
        return model.get_current_config()

    @RouteInterface.bind_route(MODULE_PREFIX, SET_ARCHITECTURE_CONFIG)
    @classmethod
    def set_architecture_config(cls, message, **kwargs) -> Result:
        '''
           Sets an architecture config
        '''
        return cls.load_and_model_call(
            message,
            cls.EXECUTABLE_CONFIG,
            model.set_current_config            
        )

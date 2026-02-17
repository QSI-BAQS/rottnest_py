'''
    This interface handles the architecture controllers
'''

from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.architecture_spec import (
    MODULE_PREFIX,
    GET_ARCHITECTURE_LIST, GET_CURRENT_ARCHITECTURE,
    SET_CURRENT_ARCHITECTURE, GET_ARCHITECTURE_CONFIG,
    SET_ARCHITECTURE_CONFIG)

# from rottnest.server.model import plugin_architecture

from rottnest.server.model import architecture as model 
from rottnest.server.responder import Result

class ArchitectureInterface(RouteInterface):
    '''
        Interface for the architecture controllers
    '''

    SELECTION_DEFAULT_NONE = ['NoArch', {
        "apimap": {
            "mask": "",
            "routes": []
        },
        "schema": {
            "name": "NoArch"
        }
    }]    
    
    ARCHITECTURE_KEY = 'architecture_key'
    ARCHITECTURE_CONFIG = 'architecture_config'
    _module_prefix = MODULE_PREFIX
    
    @RouteInterface.bind_route(MODULE_PREFIX, GET_ARCHITECTURE_LIST)
    @classmethod
    def get_architecture_list(cls, message, **kwargs) -> Result:
        '''
            Gets the list of architectures
        '''
        return Result.Ok(list(map(lambda a : a,
                        model.get_architecture_list())))

    @RouteInterface.bind_route(MODULE_PREFIX, GET_CURRENT_ARCHITECTURE)
    @classmethod
    def get_current_architecture(cls, message, **kwargs) -> Result:
        '''
           Gets the current architecture -> Returns a string
        '''
        result = model.get_current_architecture()
        if result is None:
            return Result.Error(ArchitectureInterface.SELECTION_DEFAULT_NONE)
        else:
            return Result.Ok(result)

    @RouteInterface.bind_route(MODULE_PREFIX, SET_CURRENT_ARCHITECTURE)
    @classmethod
    def set_architecture(cls, message, **kwargs) -> Result:
        '''
           Sets the current architecture
        '''
        # NOTE: Possibly to send back data from this method
        cls.load_and_model_call(
            message,
            cls.ARCHITECTURE_KEY,
            model.set_current_architecture
        )
        return cls.get_current_architecture(message, **kwargs)

    @RouteInterface.bind_route(MODULE_PREFIX, GET_ARCHITECTURE_CONFIG)
    @classmethod
    def get_architecture_config(cls, message, **kwargs) -> Result:
        '''
           Gets an architecture config
        '''
        return Result.Ok(model.get_current_config())

    @RouteInterface.bind_route(MODULE_PREFIX, SET_ARCHITECTURE_CONFIG)
    @classmethod
    def set_architecture_config(cls, message, **kwargs) -> Result:
        '''
           Sets an architecture config
        '''
        # NOTE: Possibly to send back data from this method
        cls.load_and_model_call(
            message,
            cls.ARCHITECTURE_CONFIG,
            model.set_current_config            
        )
        return cls.get_architecture_config(message, **kwargs)

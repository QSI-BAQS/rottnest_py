'''
    This interface handles the architecture controllers
'''

from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.architecture_spec import (
    GET_ARCHITECTURE_LIST, GET_ARCHITECTURE,
    SET_ARCHITECTURE, GET_ARCHITECTURE_CONFIG,
    SET_ARCHITECTURE_CONFIG)

from rottnest.server.model import plugin_architecture
from rottnest.server.responder import Result

class ArchitectureInterface(RouteInterface):
    '''
        Interface for the architecture controllers
    '''

    @RouteInterface.bind_route(GET_ARCHITECTURE_LIST)
    @classmethod
    def get_architecture_list(cls, message, **kwargs) -> Result:
        '''
            Gets the list of architectures
        '''

    @RouteInterface.bind_route(GET_ARCHITECTURE)
    @classmethod
    def get_architecture(cls, message, **kwargs) -> Result:
        '''
           Gets a particular architecture 
        '''

    @RouteInterface.bind_route(SET_ARCHITECTURE)
    @classmethod
    def set_architecture(cls, message, **kwargs) -> Result:
        '''
           Sets an architecture
        '''

    @RouteInterface.bind_route(GET_ARCHITECTURE_CONFIG)
    @classmethod
    def get_architecture_config(cls, message, **kwargs) -> Result:
        '''
           Gets an architecture config
        '''


    @RouteInterface.bind_route(SET_ARCHITECTURE_CONFIG)
    @classmethod
    def set_architecture_config(cls, message, **kwargs) -> Result:
        '''
           Sets an architecture config
        '''

'''
    This interface handles the executable controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.executable_spec import EXECUTABLE_LIST_GET, EXECUTABLE_CURRENT_GET, EXECUTABLE_CURRENT_SET, EXECUTABLE_CONFIG_GET, EXECUTABLE_CONFIG_SET 

from rottnest.server.model import plugin_architecture
from rottnest.server.responder import responder, Result


class ExecutableInterface(RouteInterface):
    '''
        Interface for the executable controllers
    '''
   
    @RouteInterface.bind_route(EXECUTABLE_LIST_GET) 
    @classmethod
    def get_executable_list(cls, message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded executables
        '''
        pass

    @RouteInterface.bind_route(EXECUTABLE_CURRENT_GET) 
    @classmethod
    def get_current_executable(cls, message, **kwargs) -> Result:
        '''
            Gets the currently loaded executable
        '''
        pass

    @RouteInterface.bind_route(EXECUTABLE_CURRENT_SET) 
    @classmethod
    def set_current_executable(cls, message, **kwargs) -> Result:
        '''
            Sets the current executable
        '''
        pass

    @RouteInterface.bind_route(EXECUTABLE_CONFIG_GET) 
    @classmethod
    def get_current_config(cls, message, **kwargs) -> Result:
        '''
            Gets the configuration options for the 
             current executable
        '''
        pass

    @RouteInterface.bind_route(EXECUTABLE_CONFIG_SET) 
    @classmethod
    def set_current_config(cls, message, **kwargs) -> Result:
        '''
            Sets the configuration options for the 
             current executable
        '''
        pass

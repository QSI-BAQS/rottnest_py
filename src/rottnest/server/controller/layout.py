'''
    This interface handles the layout controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.layout_spec import MODULE_PREFIX, SET_LAYOUT, RUN_LAYOUT

from rottnest.server.model import plugin_architecture
from rottnest.server.responder import responder, Result


class LayoutInterface(RouteInterface):
    '''
        Interface for the layout controllers
    '''
   
    @RouteInterface.bind_route(MODULE_PREFIX, SET_LAYOUT) 
    @classmethod
    def set_layout(cls, message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded layouts
        '''
        pass

    @RouteInterface.bind_route(MODULE_PREFIX, RUN_LAYOUT) 
    @classmethod
    def run_layout(cls, message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded layouts
        '''
        pass

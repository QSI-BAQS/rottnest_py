'''
    This interface handles the layout controllers 
'''
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.layout_spec import MODULE_PREFIX, SET_LAYOUT, RUN_LAYOUT

from rottnest.server.model import layout as model 
from rottnest.server.responder import responder

from rottnest.server.util.result import Result


class LayoutInterface(RouteInterface):
    '''
        Interface for the layout controllers
    '''

    SET_LAYOUT_KEY = 'layout'
   
    @RouteInterface.bind_route(MODULE_PREFIX, SET_LAYOUT) 
    @classmethod
    def set_layout(cls, message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded layouts
        '''
        return Result.Ok(cls.load_and_model_call(
            message,
            cls.SET_LAYOUT_KEY,
            model.set_layout
        ))

    @RouteInterface.bind_route(MODULE_PREFIX, RUN_LAYOUT) 
    @classmethod
    def run_layout(cls, message, **kwargs) -> Result:
        '''
            Runs the layout that has been designed against a circuit
        '''
        # TODO: This needs to completed!
        model.run_layout()

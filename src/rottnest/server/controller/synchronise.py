'''
    This interface handles the callgraph controllers 
'''
from rottnest.server.util.result import Result
from rottnest.server.model.callgraph import CallGraphModel
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.synchronise_spec import ( 
    MODULE_PREFIX,
    SYNCH_LOAD,
    SYNCH_INFO
)

SYNCRHONISE_KEY = 'payload'
SYNCRHONISE_LOAD = "load"

class SynchroniseInterface(RouteInterface):
    '''
        Interface for the callgraph controllers
    '''
    _module_prefix = MODULE_PREFIX 
   
    @RouteInterface.bind_route(MODULE_PREFIX, SYNCH_LOAD) 
    @classmethod
    def load(cls, message, **kwargs) -> Result:
        '''
            Retrieves all the necessary state information
            to set the frontend and load the data
        '''
        pass
                
    
            
    @RouteInterface.bind_route(MODULE_PREFIX, SYNCH_INFO) 
    @classmethod
    def info(cls, message, **kwargs) -> Result:
        '''
        '''
        pass





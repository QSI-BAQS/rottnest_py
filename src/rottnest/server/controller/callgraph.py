'''
    This interface handles the callgraph controllers 
'''

from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.callgraph_spec import ( 
    MODULE_PREFIX,
    GET_ROOT_GRAPH,
    GET_GRAPH,
    GET_STATUS,
    RUN_GRAPH_NODE
) 
  
from rottnest.server.model import plugin_architecture
from rottnest.server.responder import responder

from rottnest.server.util.result import Result


class CallGraphInterface(RouteInterface):
    '''
        Interface for the callgraph controllers
    '''
    _module_prefix = MODULE_PREFIX 
   
    @RouteInterface.bind_route(MODULE_PREFIX, GET_ROOT_GRAPH) 
    @classmethod
    def get_root_graph(cls, message, **kwargs) -> Result:
        pass

    @RouteInterface.bind_route(MODULE_PREFIX, GET_GRAPH) 
    @classmethod
    def get_graph(cls, message, **kwargs) -> Result:
        pass

    @RouteInterface.bind_route(MODULE_PREFIX, GET_STATUS) 
    @classmethod
    def get_status(cls, message, **kwargs) -> Result:
        pass

    @RouteInterface.bind_route(MODULE_PREFIX, RUN_GRAPH_NODE) 
    @classmethod
    def run_graph_node(cls, message, **kwargs) -> Result:
        pass

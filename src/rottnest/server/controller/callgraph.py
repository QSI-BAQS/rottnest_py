'''
    This interface handles the callgraph controllers 
'''
from rottnest.server.util.result import Result
from rottnest.server.model.callgraph import CallGraphModel
from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.callgraph_spec import ( 
    MODULE_PREFIX,
    GET_ROOT_GRAPH,
    GET_GRAPH,
    GET_STATUS,
    RUN_GRAPH_NODE
)

CALLGRAPH_PAYLOAD = 'payload'
CALLGRAPH_GRAPH_ID = 'graph_id'
CALLGRAPH_HASH = 'rottnest_hash'


class CallGraphInterface(RouteInterface):
    '''
        Interface for the callgraph controllers
    '''
    _module_prefix = MODULE_PREFIX 
   
    @RouteInterface.bind_route(MODULE_PREFIX, GET_ROOT_GRAPH) 
    @classmethod
    def get_root_graph(cls, message, **kwargs) -> Result:
        '''
            Gets the root graph to allow for the beginning of the traversal
        '''
        callgraph_packet = CallGraphModel.get_root_graph_result()
        return Result.Ok(callgraph_packet)
                
    
    @RouteInterface.bind_route(MODULE_PREFIX, GET_GRAPH) 
    @classmethod
    def get_graph(cls, message, **kwargs) -> Result:
        '''
           Gets a graph within the callgraph 
        '''
        graph_id = message[CALLGRAPH_PAYLOAD][CALLGRAPH_GRAPH_ID]
        
        
        callgraph_packet = CallGraphModel.get_graph_result(graph_id)
        return Result.Ok(callgraph_packet)

    @RouteInterface.bind_route(MODULE_PREFIX, GET_STATUS) 
    @classmethod
    def get_graph_node_status(cls, message, **kwargs) -> Result:
        '''
            Gets a status of a particular node within the graph
            NOTE: Not sure if this is even used these days
        '''
        graph_id = message[CALLGRAPH_PAYLOAD][CALLGRAPH_GRAPH_ID]
        rottnest_hash = message[CALLGRAPH_PAYLOAD][CALLGRAPH_HASH]
        
        callgraph_packet = CallGraphModel.get_node_status(graph_id, rottnest_hash)
        
        return Result.Ok(callgraph_packet)
            
    @RouteInterface.bind_route(MODULE_PREFIX, RUN_GRAPH_NODE) 
    @classmethod
    def run_graph_node(cls, message, **kwargs) -> Result:
        '''
           Runs the graph node - Will need some clarification on this
           but it should also get the visual object from it 
            TODO: Still needs to be finished
        '''
        graph_id = message[CALLGRAPH_PAYLOAD][CALLGRAPH_GRAPH_ID]

        callgraph_packet = CallGraphModel.run_graph_node(graph_id)

        return Result.Ok(callgraph_packet)


'''
    This interface handles the callgraph controllers 
'''
from enum import Enum

from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.callgraph_spec import ( 
    MODULE_PREFIX,
    GET_ROOT_GRAPH,
    GET_GRAPH,
    GET_STATUS,
    RUN_GRAPH_NODE
) # NOTE: These may have be unused now
  
# from rottnest.server.model import plugin_architecture
# from rottnest.server.responder import responder

from rottnest.server.util.result import Result

from rottnest.server.model.callgraph import CallGraphModel

RUN_GRAPH_NODE_ERROR_MESSAGE = 'Unable to run the graph node specified'
RUN_GRAPH_RUN_CONFIRMATION_MESSAGE = 'This node has been queued to re-run'


class CallGraphPacketKind(Enum):
    '''
      Enum that represents the packet kind  
    '''

    RootGraph = 'root_graph'
    Graph = 'graph'
    Node = 'node'
    RunConfirmation = 'run_confirmation'
    Error = 'error'
    
    

class CallGraphPacketBuilder:

    def __init__(self):
        '''
           Initialises the packet builder 
        '''
        self.packet_kind = CallGraphPacketKind.Error
        self.result_package = None
        self.message = ''

    @classmethod
    def make(cls):
        '''
           Part of the construction of the callgraph  
        '''
        return CallGraphPacketBuilder()

    def build(self):
        '''
           Builds the packet to be sent to the frontend 
        '''
        if self.packet_kind in { CallGraphPacketKind.Graph,
            CallGraphPacketKind.RootGraph, CallGraphPacketKind.Node }:
            return {
                'kind' : self.packet_kind,
                'result' : self.result_package
            }
        else:
            return {
                'kind' : self.packet_kind,
                'error' : self.message
            }

    def set_error(self, msg = ''):
        '''
           Sets the packet kind as an error and erases the result 
        '''

        self.packet_kind = CallGraphPacketKind.Error
        self.result_package = None
        self.message = msg
        return self

    def set_root_graph(self, graph):
        '''
           Sets the packet to show if it is a root graph 
        '''
        self.packet_kind = CallGraphPacketKind.RootGraph
        self.result_package = graph
        return self

    def set_graph(self, graph):
        '''
           Will revert and no longer be set as an error in this situation 
        '''
        self.result_package = graph
        self.packet_kind = CallGraphPacketKind.Graph
        return self

    def set_run_confirmation(self, msg='Run has been confirmed'):
        '''
           Confirms if a run was successful 
        '''
        self.packet_kind = CallGraphPacketKind.RunConfirmation
        self.message = msg

    def set_node(self, node):
        '''
           Will revert and no longer be set as an error in this situation 
        '''
        self.result_package = node
        self.packet_kind = CallGraphPacketKind.Node
        return self

class CallGraphInterface(RouteInterface):
    '''
        Interface for the callgraph controllers
    '''
    _module_prefix = MODULE_PREFIX 
   
    @RouteInterface.bind_route(MODULE_PREFIX, GET_ROOT_GRAPH) 
    @classmethod
    def get_root_graph(cls, message, **kwargs) -> Result:
        root_graph = CallGraphModel.get_root_graph_result()
        callgraph_packet = CallGraphPacketBuilder.make()
        
        if root_graph is None:
            return Result.Ok(callgraph_packet.set_error().build())
        else:
            return Result.Ok(callgraph_packet.set_root_graph(root_graph) \
                .build())
                
    
    @RouteInterface.bind_route(MODULE_PREFIX, GET_GRAPH) 
    @classmethod
    def get_graph(cls, message, **kwargs) -> Result:
        id = kwargs['graph_id']
        # min_amt = kwargs['graph_min']
        # max_amt = kwargs['graph_max']
        
        # graph_result = CallGraphModel.get_graph(id, (min_amt, max_amt))
        graph_result = CallGraphModel.get_graph_result(id)
        callgraph_packet = CallGraphPacketBuilder.make()
        
        if graph_result is None:
            return Result.Ok(callgraph_packet.set_error().build())
        else:
            return Result.Ok(callgraph_packet.set_graph(graph_result) \
                .build())

    @RouteInterface.bind_route(MODULE_PREFIX, GET_STATUS) 
    @classmethod
    def get_status(cls, message, **kwargs) -> Result:
        graph_id = kwargs['graph_id']
        element_id = kwargs['element_id']

        status_result = CallGraphModel.get_node_status(graph_id, element_id)
        
        callgraph_packet = CallGraphPacketBuilder.make()
        
        if status_result is None:
            return Result.Ok(callgraph_packet.set_error().build())
        else:
            return Result.Ok(callgraph_packet.set_node(status_result) \
                .build())
            
        pass

    @RouteInterface.bind_route(MODULE_PREFIX, RUN_GRAPH_NODE) 
    @classmethod
    def run_graph_node(cls, message, **kwargs) -> Result:
        '''
           Runs the graph node - Will need some clarification on this
           but it should also get the visual object from it 
        '''
        graph_id = kwargs['graph_id']
        element_id = kwargs['element_id']
        confirmation_result = CallGraphModel.run_graph_node(graph_id, element_id)
        callgraph_packet = CallGraphPacketBuilder.make()

        if confirmation_result is False:
            return Result.Ok(callgraph_packet.set_error(
                                 RUN_GRAPH_NODE_ERROR_MESSAGE
                             ))
        else:
            return Result.Ok(callgraph_packet.set_run_confirmation(
                                 RUN_GRAPH_RUN_CONFIRMATION_MESSAGE
                             ))
            

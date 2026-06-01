
from rottnest.server.protocol.net import Rottnest
from enum import Enum
import json

RUN_GRAPH_NODE_ERROR_MESSAGE = 'Unable to run the graph node specified'
RUN_GRAPH_RUN_CONFIRMATION_MESSAGE = 'This node has been queued to re-run'


class CallGraphPacketKind(Enum):
    '''
      Enum that represents the packet kind  
    '''

    RootGraph = 'root_graph'
    Graph = 'graph'
    Node = 'node'
    VisualObject = 'visual_object'
    GetGraphConfirmation = 'get_graph_confirmation'
    GetVisualisationConfirmation = 'get_visualisation_confirmation'
    RunNodeConfirmation = 'run_node_confirmation'
    GraphNotReady = 'graph_not_ready'
    GraphUnavailable = 'graph_unavailable'
    VisualisationNotReady = 'visualisation_not_ready'
    Compiling = 'node_compiling'
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

    
    def build_and_package(self):
        '''
            Builds and packages the packet to be sendable over a websocket
        '''
        package = self.build()

        return json.dumps({
                              "message": Rottnest.callgraph.get_graph,
                              "payload": package
                          })

        
    def build(self):
        '''
           Builds the packet to be sent to the frontend 
        '''
        packet_kind_str = self.packet_kind.name
        if self.packet_kind in { CallGraphPacketKind.Graph,
            CallGraphPacketKind.RootGraph, CallGraphPacketKind.Node,
            CallGraphPacketKind.VisualObject }:
            return {
                'kind' : packet_kind_str,
                'result' : self.result_package
            }
        if self.packet_kind in { CallGraphPacketKind.RunNodeConfirmation,
            CallGraphPacketKind.GraphNotReady, CallGraphPacketKind.GetGraphConfirmation }:
            return {
                'kind' : packet_kind_str,
                'message' : self.message
            }
        else:
            return {
                'kind' : packet_kind_str,
                'error' : self.message
            }

    def set_graph_not_ready(self, msg='Graph is not ready'):
        '''
           Sets the graph is not ready state 
        '''
        self.packet_kind = CallGraphPacketKind.GraphNotReady
        self.result_package = None
        self.message = msg
        return self

    def set_graph_unavailable(self, msg="Graph is unavailable"):
        '''
           Sets the graph to be unavailable for the frontend 
        '''
        self.packet_kind = CallGraphPacketKind.GraphUnavailable
        self.result_package = None
        self.message = msg
        return self
    
    def set_runnode_not_ready(self, msg='Visualisation is not ready'):
        '''
           Sets the graph is not ready state 
        '''
        self.packet_kind = CallGraphPacketKind.VisualisationNotReady
        self.result_package = None
        self.message = msg
        return self


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
        self.packet_kind = CallGraphPacketKind.RunNodeConfirmation
        self.message = msg
        return self
        
    def set_get_graph_confirmation(self, msg='Attempting to retrieve graph'):
        '''
           Confirms if a run was successful 
        '''
        self.packet_kind = CallGraphPacketKind.GetGraphConfirmation
        self.message = msg
        return self
    
    def set_get_run_node_confirmation(self, msg='Attempting to run node and get visual object'):
        '''
           Confirms if a run was successful 
        '''
        self.packet_kind = CallGraphPacketKind.RunNodeConfirmation
        self.message = msg
        return self

    def set_node(self, node):
        '''
           Will revert and no longer be set as an error in this situation 
        '''
        self.result_package = node
        self.packet_kind = CallGraphPacketKind.Node
        return self

    def set_visualisation(self, visual_obj):
        '''
           Will revert and no longer be set as an error in this situation 
        '''
        self.result_package = visual_obj
        self.packet_kind = CallGraphPacketKind.VisualObject
        return self

    def copy(self):
        '''
           Copies the packet builder in its current state  
        '''

        builder = CallGraphPacketBuilder()
        builder.packet_kind = self.packet_kind
        builder.result_package = self.result_package
        builder.message = self.message

        return builder        

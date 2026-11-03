"""
    Model for Callgraph
"""
from rottnest.server.util.packets.callgraph import CallGraphPacketBuilder
from rottnest.server.websocket.websocket_pool import WebSocketPoolSelector
from rottnest.debug.util import with_debug_log

'''
   States for the `get_*graph` messages

   * On first call - *_IMMEDIATE_RESULT is sent - RunConfirmation
   * On poll call  - *_POLL_RESULT is sent
   * On final call - *_FINAL_RESULT is sent
'''

POLL_TIME_DELAY = 2
POLL_RETRY_COUNT = 60

STATE_CALLGRAPH_RESULTS_KEY = 'graph_results'

STATE_APPLICATION_KEY = 'application'
STATE_PROCEDURE_KEY = 'procedure'
STATE_RESULTS_KEY = 'results'
STATE_NODE_STATUS_KEY = 'node_status'
STATE_VISUALISER_KEY = 'visualiser_object'
STATE_POLL_COUNTER_KEY = 'poll_counter'

GET_GRAPH_MSG_POLL_TEMPLATE = CallGraphPacketBuilder.make().set_graph_not_ready()
GET_GRAPH_MSG_FINISH_TEMPLATE = CallGraphPacketBuilder.make()
GET_GRAPH_MSG_INVALID_TEMPLATE = CallGraphPacketBuilder.make().set_error('Graph could not be computed or returned')
GET_GRAPH_MSG_ISSUED_TEMPLATE = CallGraphPacketBuilder.make().set_get_graph_confirmation()
GET_RUN_NODE_MSG_ISSUED_TEMPLATE = CallGraphPacketBuilder.make().set_get_graph_confirmation()


class CallGraphModel:
    '''
        Singleton instance class for tracking and handling state of the
         callgraph model
        If multiple sessions are required then we can rebind from singleton to
         per-instance models.
    '''

    # Going back should flush the view cache
    view_cache = {}
    hash_cache = {}

    GRAPH_LIMIT = 100

    curr_executable_id = None


    @classmethod
    @with_debug_log()
    def get_root_graph_result(cls):
        '''
           Same as get_graph_result but will intentionally call it with
           None 
        '''
        return CallGraphModel.get_graph_result(None)

    @classmethod
    @with_debug_log()
    def get_graph_result(cls, graph_id=None):
        '''
           Alternative for the get_graph that uses the websocket
           proxy 
        '''
        websocket = WebSocketPoolSelector.get_current_websocket().get_proxy()
        websocket.CallGraph.get_graph(websocket, graph_id)
        return GET_GRAPH_MSG_ISSUED_TEMPLATE.copy().build()

        

    @classmethod
    def get_node_status(cls, graph_id, element_id):
        '''
           Gets the status of a particular node within a graph id 
        '''
        # TODO: Complete this model method
        # NOTE: This is a dummy object
        return {
            STATE_NODE_STATUS_KEY : '',
            STATE_VISUALISER_KEY : {}
        }

    @classmethod
    def run_graph_node(cls, graph_id):
        '''
           Attempts to run the graph node - True if it has been queued
            False if an error had occurred
        '''
        websocket = WebSocketPoolSelector.get_current_websocket().get_proxy()
        websocket.CallGraph.run_graph_node(websocket, graph_id)
        return GET_RUN_NODE_MSG_ISSUED_TEMPLATE.copy().build()

"""
    Model for Callgraph
"""
# from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
# from rottnest.plugins import executables as singleton
# from rottnest.server.view import callgraph as view

from rottnest.server.util.packets.callgraph import CallGraphPacketBuilder
from rottnest.procedures.procedure_manager import ProcedureManager
from rottnest.procedures.callgraph.procedure_get_graph import GetGraphProcedure
from rottnest.debug.util import with_debug_log
from rottnest.server.app.application import RottnestApplication

import time

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




@with_debug_log()
def _get_graph_result_poll(state):
    '''
        Send a heartbat to the frontend but should also
        ensure that the state is up to date for the frontend
        or sets the complete state for the procedure
    '''
    # Sleep is here to ensure that we aren't spamming the frontend with a lot
    # of rubbish
    time.sleep(POLL_TIME_DELAY)
    app = state[STATE_APPLICATION_KEY]
    proc = state[STATE_PROCEDURE_KEY]
    counter = state[STATE_POLL_COUNTER_KEY]

    
    if app is not None and proc is not None:

        if counter < POLL_RETRY_COUNT:
            state[STATE_POLL_COUNTER_KEY] = counter + 1
            proc.poll()
            wsock = app.get_websocket()
            if wsock is not None:
                graph_package = GET_GRAPH_MSG_POLL_TEMPLATE.copy().build_and_package()
                wsock.send(graph_package)
        else:
            proc.abort_procedure()
        
    

@with_debug_log()
def _get_graph_result_finalise(state):
    '''
        Gets the graph results, it should send it down once it is ready
    '''
    app = state[STATE_APPLICATION_KEY]
    proc = state[STATE_PROCEDURE_KEY]
    
    if app is not None and proc is not None:
        wsock = app.get_websocket()
        results = state[STATE_RESULTS_KEY]
        if wsock is not None:
            if results is not None:

                if proc.was_aborted():
                    graph_package = GET_GRAPH_MSG_INVALID_TEMPLATE.copy()
                else:
                    callgraph_results = results[STATE_CALLGRAPH_RESULTS_KEY]
                    if callgraph_results is not None:

                        graph_package = GET_GRAPH_MSG_FINISH_TEMPLATE.copy()\
                            .set_graph(callgraph_results).build_and_package()

            # Sends valid or invalid package
            wsock.send(graph_package.build_and_package())

    
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

    # @classmethod
    # def generate_root_node(cls):
    #     '''
    #         Generates the root node of the graph
    #     '''
    #     parser = PyliqtrParser(
    #         singleton.get_current_executable()
    #     )
    #     parser.parse()
    #     return parser

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
           Gets the graph, if it is None it will get the root graph
           If it the graph id is a valid integer it will retrieve
           the callgraph associated
        '''
        app = RottnestApplication.get_instance()
        proc_manager = ProcedureManager.get_instance()

        result_dict = dict()
        state_obj = {
            STATE_APPLICATION_KEY: app,
            STATE_RESULTS_KEY: result_dict,
            STATE_POLL_COUNTER_KEY: 0
        }
        getgraph_proc = GetGraphProcedure.construct_get_graph_proc(state_obj,
                                                                   graph_id)
        state_obj[STATE_PROCEDURE_KEY] = getgraph_proc


        _result = proc_manager.execute_defer(getgraph_proc,
                                             _get_graph_result_poll,
                                             _get_graph_result_finalise,
                                             state_obj)
        
        return GET_GRAPH_MSG_ISSUED_TEMPLATE.copy().build()

        
    # @classmethod
    # def get_graph(
    #     cls,
    #     graph_id: str,
    #     graph_limit_range: tuple  # (0, cls.GRAPH_LIMIT)
    # ):
    #     '''
    #         Gets a pylitrq parser object from a graph_id
    #     '''

    #     # If no ID is passed, then this is a root node
    #     if graph_id is None:
    #         prefix = ''
    #         parser = cls.generate_root_node()
    #         cls.curr_executable_id = id(singleton.get_current_executable)

    #     # Non-root request
    #     else:

    #         # Check that the executable hasn't been changed
    #         if cls.curr_executable_id != id(singleton.get_current_executable):
    #             # TODO View error handling
    #             return None

    #         # Collect the correct paraser and set up the prefix
    #         prefix = graph_id
    #         parser = cls.view_cache[graph_id].parser

    #     # Create a graph view object and a prefix counter
    #     graph = []
    #     count = 0

    #     for node in parser.unroll_graph(prefix=prefix):
    #         count += 1

    #         if count > cls.GRAPH_LIMIT:
    #             break

    #         handle_id = node.handle_id
    #         expands = False

    #         if node.rottnest_hash is not None:
    #             expands = True
    #             if (
    #                 node.name is None
    #                 or node.rottnest_hash in cls.hash_cache
    #                ):  # Cache without name triggers cache load
    #                 node = cls.hash_cache[node.rottnest_hash]

    #             else:  # Cache with name triggers cache set
    #                 # Node triggers cache update
    #                 cls.hash_cache[node.rottnest_hash] = node
    #         if node.rottnest_hash is None:
    #             expands = False

    #         # Populate the view cache
    #         cls.view_cache[handle_id] = node

    #         graph.append(
    #             view.callgraph_node(
    #                 node.name,
    #                 node.description,
    #                 [],
    #                 handle_id,
    #                 expands,
    #             )
    #         )
    #     graph_segment = view.callgraph_segment(0, graph)

    #     return graph_segment

    @classmethod
    def get_node_status(cls, graph_id, element_id):
        '''
           Gets the status of a particular node within a graph id 
        '''
        # TODO: Complete this model method
        # NOTE: This is a dummy object
        return {
            STATE_NODE_STATUS_KEY : 'Something',
            STATE_VISUALISER_KEY : {}
        }

    @classmethod
    def run_graph_node(cls, graph_id, element_id):
        '''
           Attempts to run the graph node - True if it has been queued
            False if an error had occurred
        '''
        # TODO: Complete this model method
        return False

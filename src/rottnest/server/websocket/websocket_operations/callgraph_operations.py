from rottnest.procedures.visualiser.procedure_get_visualiser import GetVisualiserProcedure
from rottnest.server.util.packets.callgraph import CallGraphPacketBuilder
from rottnest.procedures.callgraph.procedure_get_graph import GetGraphProcedure
from rottnest.server.protocol.operation import CallGraph as SpecOperations
from rottnest.server.websocket.websocket_operations.operations_spec import \
     WebSocketOperationsSpecification

from rottnest.procedures.procedure_manager.mpsc_common import MPSC_CALLGRAPH_CHANNEL_TAG, MPSC_VISUALISER_CHANNEL_TAG
from rottnest.procedures.procedure_manager.mpsc_channel import MPSCChannelProvider
from rottnest.procedures.procedure_manager import ProcedureManagerSelector

import time
    
POLL_TIME_DELAY = 2
POLL_RETRY_COUNT = 60

STATE_CALLGRAPH_RESULTS_KEY = 'graph_results'
STATE_NODE_STATUS_KEY = 'node_status'
STATE_VISUALISER_KEY = 'visualiser_object'
STATE_POLL_COUNTER_KEY = 'poll_counter'

GET_RUNNODE_MSG_POLL_TEMPLATE = CallGraphPacketBuilder.make().set_runnode_not_ready()
GET_RUNNODE_MSG_FINISH_TEMPLATE = CallGraphPacketBuilder.make()
GET_RUNNODE_MSG_INVALID_TEMPLATE = CallGraphPacketBuilder.make().set_error('Visualisation could not be computed or returned')
GET_RUNNODE_MSG_ISSUED_TEMPLATE = CallGraphPacketBuilder.make().set_get_run_node_confirmation()

GET_GRAPH_MSG_POLL_TEMPLATE = CallGraphPacketBuilder.make().set_graph_not_ready()
GET_GRAPH_MSG_FINISH_TEMPLATE = CallGraphPacketBuilder.make()
GET_GRAPH_MSG_INVALID_TEMPLATE = CallGraphPacketBuilder.make().set_error('Graph could not be computed or returned')
GET_GRAPH_MSG_ISSUED_TEMPLATE = CallGraphPacketBuilder.make().set_get_graph_confirmation()

TRANSLATE_HANDLE = 'handle_id'
TRANSLATE_NAME = 'name'
TRANSLATE_DESC = 'description'
TRANSLATE_HASH = 'rottnest_hash'
TRANSLATE_EXPANDS = 'expands'


class GetGraphStateObject():
    '''
       State object that is constructed for this purpose 
    '''

    def __init__(self, websocket, procedure, reader, limit: int):
        '''
           Stores the websocket and procedure
           Initialises state information it will need to maintain per instance 
        '''
        self.websocket = websocket
        self.procedure = procedure
        self.reader = reader
        self.counter = 0
        self.limit = limit

    def get_websocket_proxy(self):
        '''
           Gets the websocket proxy 
        '''
        return self.websocket

    def get_procedure(self):
        '''
           Gets the procedure 
        '''
        return self.procedure

    def get_limit(self):
        '''
           Gets the limit of the counter 
        '''
        return self.limit


    def get_counter(self):
        '''
           Gets the counter of the state object before aborting 
        '''
        return self.counter

    def increment_counter(self):
        '''
           Increments the counter by 1 
        '''
        self.counter += 1

    
    def get_reader(self):
        '''
           Returns the reader 
        '''
        return self.reader


class CallGraphOperations(WebSocketOperationsSpecification):
    '''
        CallGraphOperations - Ensures the spec is implemented and checked
    '''

    OPERATIONS = SpecOperations

    def __init__(self):
        '''
           Initialises operations object and checks to see
           if the set of operations matches the methods expected 
        '''
        super().__init__(self.__class__)


    def get_root_graph(self, websocket):
        '''
           Gets the root graph
               1. root_graph call is equivalent to get_graph call on 0
               2. Will just perform the call on get_graph as necessary
                   
        '''
        return self.get_graph(websocket, None)
        
    def get_status(self):
        '''
           Get Status, current it does not do anything 
        '''
        pass
    
    def get_graph(self, websocket, graph_id=None):
        '''
           Gets the graph object 
        '''
        proc_manager = ProcedureManagerSelector.get_instance().get_default()

        mpsc_provider: MPSCChannelProvider = MPSCChannelProvider.get_instance()
        mpsc_provider.recreate_channel(MPSC_CALLGRAPH_CHANNEL_TAG)
        mpsc_reader, _mpscstate = mpsc_provider.get_reader(MPSC_CALLGRAPH_CHANNEL_TAG)


        getgraph_proc = GetGraphProcedure(graph_id=graph_id)

        state_object = GetGraphStateObject(websocket,
                                        getgraph_proc,
                                        mpsc_reader,
                                        POLL_RETRY_COUNT)


        proc_manager.dispatch(
                            getgraph_proc,
                            self.get_graph_poll,
                            None,
                            self.get_graph_finalise,
                            state_object)

        return GET_GRAPH_MSG_ISSUED_TEMPLATE.copy().build()

    def run_graph_node(self, websocket, graph_id):
        '''
           Runs the graph node itself - Will retrieve the visualiser
           object and allow it to be viewable
        '''
        proc_manager = ProcedureManagerSelector.get_instance().get_default()

        mpsc_provider: MPSCChannelProvider = MPSCChannelProvider.get_instance()
        mpsc_provider.recreate_channel(MPSC_VISUALISER_CHANNEL_TAG)
        mpsc_reader, _mpscstate = mpsc_provider.get_reader(MPSC_VISUALISER_CHANNEL_TAG)

        runnode_proc = GetVisualiserProcedure(graph_id=graph_id)


        state_object = GetGraphStateObject(websocket,
                                        runnode_proc,
                                        mpsc_reader,
                                        POLL_RETRY_COUNT)
        proc_manager.dispatch(
                            runnode_proc,
                            self.get_visualisation_poll,
                            None,
                            self.get_visualisation_finalise,
                            state_object)
        return GET_RUNNODE_MSG_ISSUED_TEMPLATE.copy().build()

    def get_visualisation_poll(self, state_object: GetGraphStateObject):
        '''
           Gets the visualisation object 
        '''
        wproxy = state_object.get_websocket_proxy()
        wsock = wproxy.get_websocket()
        proc = state_object.get_procedure()
        counter = state_object.get_counter()
        limit = state_object.get_limit()
        actions = wproxy.get_actions()

        if counter < limit:
            state_object.increment_counter()
            proc.poll()
            time.sleep(POLL_TIME_DELAY)
            graph_package = GET_RUNNODE_MSG_POLL_TEMPLATE.copy()\
                .build_and_package()
            actions.websocket_write(wsock, graph_package)
        else:
            proc.abort_procedure()

        
    def get_visualisation_finalise(self, state_object: GetGraphStateObject):
        '''
           Finaliser for the procedure and when to send back 
        '''
        wproxy = state_object.get_websocket_proxy()
        wsock = wproxy.get_websocket()
        actions = wproxy.get_actions()
        reader = state_object.get_reader()
        proc = state_object.get_procedure()
        graph_package = GET_RUNNODE_MSG_INVALID_TEMPLATE.copy()
        if not proc.was_aborted():
            callgraph_results = reader.read()
            if callgraph_results is not None:
                
                item = callgraph_results.get_object()
                visual_object = item[1].vis_obj
                
                graph_package = GET_RUNNODE_MSG_FINISH_TEMPLATE.copy()\
                    .set_visualisation(visual_object)

        
        actions.websocket_write(wsock, graph_package.build_and_package())

    def get_graph_poll(self, state_object: GetGraphStateObject):
        '''
           Poll method for get_graph 
        '''
        wproxy = state_object.get_websocket_proxy()
        wsock = wproxy.get_websocket()
        proc = state_object.get_procedure()
        counter = state_object.get_counter()
        limit = state_object.get_limit()
        actions = wproxy.get_actions()

        if counter < limit:
            state_object.increment_counter()
            proc.poll()
            time.sleep(POLL_TIME_DELAY)
            graph_package = GET_GRAPH_MSG_POLL_TEMPLATE.copy()\
                .build_and_package()
            actions.websocket_write(wsock, graph_package)
        else:
            proc.abort_procedure()



    def translate_items(self, many_objects):
        '''
           Calls translate_object on all objects in the list 
        '''
        results = []
        for obj in many_objects:
            results.append(self.translate_object(obj))

        return results

    def translate_object(self, obj):
        '''
           Translate from internal representation
           that fixes the hash to use a hex string
        '''
        new_hash = None if obj[TRANSLATE_HASH] is None else obj[TRANSLATE_HASH].hex()
        expands = new_hash is not None
        return {
            TRANSLATE_HANDLE: obj[TRANSLATE_HANDLE], 
            TRANSLATE_NAME: obj[TRANSLATE_NAME], 
            TRANSLATE_DESC: obj[TRANSLATE_DESC],
            TRANSLATE_EXPANDS: expands,
            TRANSLATE_HASH: new_hash, # needed for fix
        }

    def get_graph_finalise(self, state_object: GetGraphStateObject):
        '''
           Finaliser method for get_graph 
        '''
        wproxy = state_object.get_websocket_proxy()
        wsock = wproxy.get_websocket()
        actions = wproxy.get_actions()
        reader = state_object.get_reader()
        proc = state_object.get_procedure()
        graph_package = GET_GRAPH_MSG_INVALID_TEMPLATE.copy()

        
        if not proc.was_aborted():
            callgraph_results = reader.read()
            if callgraph_results is not None:
                # NOTE: Why is the id 1?
                items = callgraph_results.get_object()[1]
                results = self.translate_items(items)
                graph_package = GET_GRAPH_MSG_FINISH_TEMPLATE.copy()\
                    .set_graph(results)

        
        actions.websocket_write(wsock, graph_package.build_and_package())

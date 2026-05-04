from rottnest.server.util.packets.callgraph import CallGraphPacketBuilder
from rottnest.procedures.callgraph.procedure_get_graph import GetGraphProcedure
from rottnest.server.protocol.operation import CallGraph as SpecOperations
from rottnest.server.websocket.websocket_operations.operations_spec import \
     WebSocketOperationsSpecification

 
from rottnest.procedures.procedure_manager import ProcedureManagerSelector
    
POLL_TIME_DELAY = 2
POLL_RETRY_COUNT = 60


STATE_CALLGRAPH_RESULTS_KEY = 'graph_results'
STATE_NODE_STATUS_KEY = 'node_status'
STATE_VISUALISER_KEY = 'visualiser_object'
STATE_POLL_COUNTER_KEY = 'poll_counter'

GET_GRAPH_MSG_POLL_TEMPLATE = CallGraphPacketBuilder.make().set_graph_not_ready()
GET_GRAPH_MSG_FINISH_TEMPLATE = CallGraphPacketBuilder.make()
GET_GRAPH_MSG_INVALID_TEMPLATE = CallGraphPacketBuilder.make().set_error('Graph could not be computed or returned')
GET_GRAPH_MSG_ISSUED_TEMPLATE = CallGraphPacketBuilder.make().set_get_graph_confirmation()


class GetGraphStateObject():
    '''
       State object that is constructed for this purpose 
    '''

    def __init__(self, websocket, procedure, limit: int, results=dict()):
        '''
           Stores the websocket and procedure
           Initialises state information it will need to maintain per instance 
        '''
        self.websocket = websocket
        self.procedure = procedure
        self.results = results if None else dict()
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

    
    def get_results(self):
        '''
           Returns the results 
        '''
        return self.results        


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

        results_dict = dict()

        getgraph_proc = GetGraphProcedure.construct_get_graph_proc(
                                        results_dict,
                                        graph_id)

        state_object = GetGraphStateObject(websocket,
                                        getgraph_proc,
                                        POLL_RETRY_COUNT,
                                        results_dict)

        proc_manager.dispatch(
                            getgraph_proc,
                            self.get_graph_poll,
                            self.get_graph_finalise,
                            state_object)

        return GET_GRAPH_MSG_ISSUED_TEMPLATE.copy().build()

    def run_graph_node(self, websocket, graph_id):
        '''
           Runs the graph node itself 
        '''
        pass

    def get_graph_poll(self, state_object: GetGraphStateObject):
        '''
           Poll method for get_graph 
        '''
        wsock = state_object.get_websocket_proxy()
        proc = state_object.get_procedure()
        counter = state_object.get_counter()
        limit = state_object.get_limit()

        if counter < limit:
            state_object.increment_counter()
            proc.poll()
            graph_package = GET_GRAPH_MSG_POLL_TEMPLATE.copy()\
                .build_and_package()
            wsock.send(graph_package)
        else:
            proc.abort_procedure()


    def get_graph_finalise(self, state_object: GetGraphStateObject):
        '''
           Finaliser method for get_graph 
        '''
        wsock = state_object.get_websocket_proxy()
        proc = state_object.get_procedure()
        results = state_object.get_results()
        graph_package = GET_GRAPH_MSG_INVALID_TEMPLATE.copy()

        if not proc.was_aborted():
            callgraph_results = results[STATE_CALLGRAPH_RESULTS_KEY]
            if callgraph_results is not None:
                graph_package = GET_GRAPH_MSG_FINISH_TEMPLATE.copy()\
                    .set_graph(callgraph_results).build_and_package()

        # Sends valid or invalid package
        wsock.send(graph_package.build_and_package())

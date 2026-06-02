from rottnest.server.protocol.operation import Layout as SpecOperations
from rottnest.server.websocket.websocket_operations.operations_spec import \
     WebSocketOperationsSpecification
from rottnest.server.protocol.net import Rottnest

STANDARD_DELAY_ON_POLL = 3

RUN_LAYOUT_MSG_END = {
    "message": Rottnest.layout.poll_status,
    "payload": "issued"
}

RUN_LAYOUT_PROCESS_MSG = {
    "message": Rottnest.layout.poll_status,
    "payload": "processing"
}

RUN_LAYOUT_EXEC_ERROR = {
    "message": Rottnest.layout.err.executable_invalid,
}

RUN_LAYOUT_ARCH_ERROR = {
    "message": Rottnest.layout.err.architecture_invalid,
}

STATE_OBJ_APP_KEY = 'application'
STATE_OBJ_PREPROC_KEY = 'preprocessor'


class RunResultHeaderTag:
    '''
       Header tag for the run results to be categorised
       broadly 
    '''
    HEADER_TAG = 'result_tag'

    RESULT_ENTRY = 'RESULT_ENTRY'
    FINAL_RESULT = 'FINAL_RESULT'

class RunLayoutStateObject:
    '''
       Protocol to ensure the interface and methods
       that need to be implemented are used
    '''

    def __init__(self, websocket_proxy, procedure, mpsc_reader):
        '''
           Initialises the object with the required proxy and procedure 
        '''
        self.websocket_proxy = websocket_proxy
        self.procedure = procedure
        self.mpsc_reader = mpsc_reader

    def get_websocket_proxy(self):
        '''
           Gets the websocket proxy for the operation 
        '''
        return self.websocket_proxy

    def get_procedure(self):
        '''
           Gets the procedure needed for the operation 
        '''
        return self.procedure

    def get_reader(self):
        '''
           Gets the MPSC Reader that can be used for hooks 
        '''
        return self.mpsc_reader

class LayoutOperations(WebSocketOperationsSpecification):
    '''
        LayoutOperations - For managing and executing layouts
            that have been sent and need to be encoded
    '''

    OPERATIONS = SpecOperations

    def __init__(self):
        '''
           Initialises operations object and checks to see
           if the set of operations matches the methods expected 
        '''

        super().__init__(self.__class__)



    def set_layout(self, layout):
        '''
           Given a layout that can be set, it will provide
           a facilitate to hold and store the layouts and their status 
        '''
        pass


    def run_layout(self,
                   websocket,
                   procedure,
                   procedure_manager,
                   mpsc_reader
                   ):
        '''
           Runs the layout and maintains state information around
           the execution and provides feedback to the frontend 
        '''
        state_object = RunLayoutStateObject(websocket, procedure, mpsc_reader)
        _result = procedure_manager.dispatch(
                                procedure,
                                self.run_layout_poll_extraction,
                                self.run_layout_complete,
                                self.run_layout_finalise,
                                state_object)


        return _result

    def run_layout_complete(self, state_object: RunLayoutStateObject):
        '''
           Hook for complete method, is currently a noop 
        '''
        proc = state_object.get_procedure()        
        is_complete = proc.complete()
        return is_complete

    def run_layout_tag_output(self, entry, tag):
        '''
           Tags the object with relevant information 
        '''
        entry[RunResultHeaderTag.HEADER_TAG] = tag
        return entry

    def run_layout_write_back(self, state_object: RunLayoutStateObject,
                              is_poll=True):
        '''
           Generalisation for both poll and finalise 
        '''
        websocket_proxy = state_object.get_websocket_proxy()
        websocket = websocket_proxy.get_websocket()
        actions = websocket_proxy.get_actions()
        preproc = state_object.get_procedure()
        reader = state_object.get_reader()

        if is_poll:
            preproc.poll()

        current_messages = reader.read_all()
        header = RunResultHeaderTag.RESULT_ENTRY
        for msg in current_messages:
            result_data = msg.get_object()
            if msg.is_iterable():
                for entry in result_data:
                    result = self.run_layout_tag_output(entry,
                                header)
                    actions.websocket_result_write(websocket, result)
            else:
                header = RunResultHeaderTag.FINAL_RESULT
                result = self.run_layout_tag_output(result_data, header)
                actions.websocket_result_write(websocket, result)
                
                    

    def run_layout_poll_extraction(self, state_object: RunLayoutStateObject):
        '''
           Given a layout, the operation should attempt to poll
           the state of the execution and check to see if the layout/run is finish
           and can pull out information regarding it

           These should be the results it can extract  
        '''
        self.run_layout_write_back(state_object)
                        
    def run_layout_finalise(self, state_object: RunLayoutStateObject):
        '''
            Given a layout, it will receive the state_object
            that it can then extract the results from and send them back
            after completion of a run
            These should be the results it can extract  
        '''
        self.run_layout_write_back(state_object, is_poll=False)
        

    def poll_layout_status(self, websocket, layout_id):
        '''
           Given a layout id, it can be used to provide information
           on layout instances themselves 
        '''
        pass
        

    def poll_status(self):
        '''
           Poll status implementation, currently not implemented 
        '''
        pass


    

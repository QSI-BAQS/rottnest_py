
from geventwebsocket.websocket import WebSocket
from rottnest.server.protocol.net import Rottnest
from rottnest.server.websocket.websocket_operations import CallGraphOperations, LayoutOperations


class RottnestWebSocketCommon:
    '''
       These are common actions that would be used by
       the websocket to process the data and send the relevant
       hooks
    '''
    
    def __init__(self):
        '''
           Initialises the common actions, these will require
           a websocket to be passed into it 
        '''
        self.Callgraph = CallGraphOperations()
        self.Layout = LayoutOperations()


    def websocket_write(self, websocket: WebSocket, data):
        '''
           Raw write to the websocket using data given

           Can raise an exception if the websocket has been shutdown
           or if the data is not serialisable
        '''
        websocket.send(data)


    def websocket_read(self, websocket: WebSocket):
        '''
           Raw read of the websocket

           Can raise an exeception if the websocket has been shutdown
           or invalid 
        '''
        return websocket.receive()

    
    def websocket_stream_write(self, websocket, stream):
        '''
           Writes data to the websocket via rottnest instance
           usage is on composer streams
           NOTE: Better rename or generalise this method
        '''
        for sobj in stream:
    
            stream_tup = sobj.items()
            # unit_ids = sobj.get_compute_unit_ids()
            stream_data = dict()
            for (idx, tup) in enumerate(stream_tup):
                tkey, tvalue = tup
                stream_data[tkey] = tvalue
                # stream_data['cuid'] = unit_ids[idx]
        
            # NOTE: Results, graph_state info
            websocket.send(Rottnest\
                       .start_packet(Rottnest.data.run_result)\
                       .set_payload(stream_data)\
                       .build())

    def websocket_result_write(self, websocket, results):
        '''
            Writes data to the websocket via the rottnest instance
            On results from composer objects    
            NOTE: Better rename or generalise this method
        '''
        print("Sending")
        websocket.send(Rottnest\
                       .start_packet(Rottnest.data.run_result)\
                       .set_payload(results)\
                       .build())


    def websocket_result_final_write(self, websocket, results):
        '''
            Writes data to the websocket via the rottnest instance
            On results from composer objects    
        '''
        websocket.send(Rottnest\
                       .start_packet(Rottnest.data.run_result)\
                       .set_payload(results)\
                       .put("cu_id", "TOTAL") \
                       .build())
        

    def websocket_heartbeat(self, websocket):
        '''
           Provides a heartbeat mechanism for the websocket
           to ensure that it is kept alive
        '''
        heartbeat_package = Rottnest.make_message(Rottnest.liveness)
        wsock = websocket
        wsock.send(heartbeat_package)




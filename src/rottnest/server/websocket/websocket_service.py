from geventwebsocket.websocket import WebSocket
from gevent import Timeout

WEBSOCKET_RECEIVE_TIMEOUT = 0.5

class WebSocketWriteObject:
    '''
       WriteBufferObject for the service so it is able to
       schedule/handle it accordingly 
    '''

    def __init__(self, data, binary=None):
        '''
           Initialises the write object 
        '''
        self.data = data
        self.binary = binary

    @classmethod
    def make(cls, data, binary=None):
        '''
            Constructs write object
        '''
        return WebSocketWriteObject(data, binary)


    def get(self):
        '''
           Gets the object that is contained in here
        '''
        return self.data


    def get_binary_setting(self):
        '''
            Gets the binary parameter value
        '''
        return self.binary




class WebSocketService:
    '''
       WebSocketService - This service will handle buffers
       for sending and reading - It will wrap around and operate
       with the required operations. 
    '''


    def __init__(self, websocket: 'WebSocket'):
        '''
           WebSocketService Initialiser 
        '''
        self.write_buffer = []
        self.websocket = websocket
        self.iterable = WebSocketStateHandle.websocket_receive_yieldable(self)


    def get_buffer(self) -> list[WebSocketWriteObject]:
        '''
           Gets the buffer of the websocket objects 
        '''
        return self.write_buffer

    def get_websocket(self) -> 'WebSocket':
        '''
           Retrieves the websocket 
        '''
        return self.websocket

    def send(self, data, binary=None):
        '''
           WebSocket.send wrapper - buffers an object to be eventually
           sent by the process 
        '''
        self.write_buffer.append(WebSocketWriteObject.make(data))


    def receive(self):
        '''
            Websocket.receive wrapper - attempts to retrieve the data from
            the websocket and operate on it
        '''
        data = next(self.iterable)
        return data

        
class WebSocketStateHandle:
    '''
       Using yieldable functions to return objects
       required but also step through the operations to then send
    '''

    @staticmethod
    def websocket_operate_on_sendables(service: WebSocketService):
        '''
           Given a list of sendable objects, we will check to see
           if the buffer has elements before dequeuing and sending them back
           to the frontend 
        '''
        buffer = service.get_buffer()
        wsock = service.get_websocket()

        while len(buffer) > 0:
            obj = buffer.pop(0)
            wsdata = obj.get()
            wsbin = obj.get_binary_setting()

            wsock.send(wsdata, binary=wsbin)
            


    @staticmethod
    def websocket_receive_yieldable(service: WebSocketService):
        '''
           Yeildable Static Method - Will call send when recv has been concluded 
        '''
        while True:
            wsock = service.get_websocket()
            WebSocketStateHandle.websocket_operate_on_sendables(service)
            try:
                with Timeout(WEBSOCKET_RECEIVE_TIMEOUT) as _timeout:
                    ret_data = wsock.receive()
                    yield ret_data
            except Timeout:
                ...
        
            
            

            

    
        

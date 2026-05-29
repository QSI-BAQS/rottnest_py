from threading import Semaphore
from geventwebsocket.websocket import WebSocket
from io import StringIO
from .websocket_operations import RottnestWebSocketCommon

class RottnestWebSocketProxy(RottnestWebSocketCommon):
    '''
       Used to hold onto the websocket methods
       and default interactions 
    '''
    def __init__(self, websocket: WebSocket | None = None,
                 websocket_semaphore: Semaphore | None = None):
        '''
            Initialises the websocket proxy that will mediate
            interaction between the rottnest application
            and websocket itself

            It should be responsible for the operations within here
            rather than the websocket itself
        '''
        self.tracking_id: int | None = None
        self.websocket = websocket
        self.semaphore = websocket_semaphore
        super().__init__()

    @classmethod
    def make_uninitialised():
        '''
           Do note, this mechanism is only for testing and mock devices
           that are to provide some level of introspection within the system
           itself
        '''
        proxy = RottnestWebSocketProxy(WebSocket(None, StringIO(''), Semaphore()))
        return proxy


    def set_tracking_id(self, trackingid):
        '''
           Sets a tracking id for the websocket which is used by memory/management pools
        '''
        self.tracking_id = trackingid
        

    def get_actions(self) -> RottnestWebSocketCommon:
        '''
            Get an actions object that will have a common methods one would use
            with a websocket on this server
        '''
        return self

    def get_websocket(self):
        '''
           Gets the websocket attached to the proxy 
        '''
        return self.websocket

from .websocket_proxy import RottnestWebSocketProxy

class WebSocketPoolSelector:
    '''
       Selector class with simple methods that then returns the
       appropriate object 
    '''

    @classmethod
    def get_current_websocket(cls):
        '''
           Gets the single websocket that is active through out the application 
        '''
        return CurrentWebSocketSingleton.get_instance()

    @classmethod
    def get_websocket_pool(cls):
        '''
           Gets the WebSocket pool singleton 
        '''
        return WebSocketPoolSingleton.get_instance()


class WebSocketPoolSingleton:
    '''
       WebSocketPool Singleton
       This is used to manage the pool of sockets and reference it where
       needed within the server context 
    '''
    @classmethod
    def get_instance(cls):
        '''
           Gets the instance of the websocket pool 
        '''
        raise NotImplementedError

class CurrentWebSocketSingleton:
    '''
        Single WebSocket singleton instance that can be
        spawned and used through out the system
    '''

    _instance = None

    def __init__(self, websocket_proxy=None):
        '''
            Initialise websocket
        '''
        self.websocket = websocket_proxy

    def and_with(self, websocket, semaphore):
        '''
           Chained method that sets the interrior of the proxy
        '''
        self.websocket = RottnestWebSocketProxy(websocket, semaphore)
        return self
        
    def set_current_websocket(self, websocket_proxy):
        '''
           Updates the instance with a new websocket proxy 
        '''
        CurrentWebSocketSingleton._instance = websocket_proxy

    def get_proxy(self):
        '''
           Gets the websocket proxy object 
        '''
        return self.websocket

    @classmethod
    def get_instance(cls):
        '''
           Gets the instance of the websocket 
        '''
        if CurrentWebSocketSingleton._instance is None:
            CurrentWebSocketSingleton._instance = CurrentWebSocketSingleton()
        return CurrentWebSocketSingleton._instance

class WebSocketPool:
    '''
       WebsocketPool which is used to manage
       connections and the state as well as manage

       At the moment we will not need to utilise this until much alter 
    '''

    def __init__(self):
        '''
           WebSocketPool - It will manage a number of websockets but also check
           to see if it is active or not
        '''
        self._NEXT_ID = 1
        self.websockets_map: dict[int, RottnestWebSocketProxy] = list()

    def _next_id(self):
        '''
           Numbered sequence within the pool itself 
        '''
        to_return = self._NEXT_ID
        self._NEXT_ID = to_return + 1
        return to_return
    

    def register_websocket(self,
                websocket_proxy: RottnestWebSocketProxy) -> tuple[bool, int | None]:
        '''
           Registers a websocket with the websocket pool that will be managed
           when there are multiple participants on the system 
        '''
        next_id = self._next_id()
        self.websockets_map[next_id] = websocket_proxy
        websocket_proxy.set_tracking_id(next_id)
        return (True, next_id)

    def get_websocket_proxy(self, websocket_id: int) -> RottnestWebSocketProxy | None:
        '''
           Gets a websocket proxy if the id matches the key within the map itself
           if not, it will return None 
        '''
        if websocket_id in self.websockets_map:
            result = self.websockets_map[websocket_id]
            return result
        else:
            return None

    
    def unregister_websocket(self, websocket_id: int) -> bool:
        '''
           Unregisters the websocket that has been associated with the pool 
        '''
        if websocket_id in self.websockets_map:
            del self.websockets_map[websocket_id]
            return True
        else:
            return False

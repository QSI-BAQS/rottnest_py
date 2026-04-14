"""
    Rottnest application class
"""
from io import StringIO
from geventwebsocket.websocket import WebSocket
from threading import Semaphore
from rottnest.server.app.app_config import ApplicationConfig, AppExtensions
from rottnest.debug.monitor import DebugMonitor
from rottnest.server.protocol.net import Rottnest

class RottnestApplicationUnavailableException(BaseException):

    UnavailableMessage = "Unable to retrieve instance when no object has been made"
    
    def __init__(self, message=UnavailableMessage):
        super().__init__(message)

class RottnestApplication:
    """
        Application class
        Acts as a simple map 
        To have more concrete information provided later
    """

    _appinstance: type['RottnestApplication'] | None = None
    
    def __init__(
            self,
            wsock,
            wsock_sem,
            apploader=ApplicationConfig.default(),
            is_uninit=False
        ):
        """
            Initialises an application
            with simple dictionary that will
            map arbitrary objects
            ApplicationConfig will load defaults or
            what is specified
        """
        self.wsock = wsock
        self.wsock_sem = wsock_sem
        self.is_uninit = is_uninit
        self.app_state_map = {}
        self.app_extensions = AppExtensions()
        apploader.load_and_attach(self.app_extensions)
        DebugMonitor.current().set_console_context(self)
        DebugMonitor.current().get_console().set_app(self)

        if RottnestApplication._appinstance is None \
            or RottnestApplication._appinstance.is_uninit:
            RottnestApplication._appinstance = self
            


    @classmethod
    def try_get_instance(cls):
        '''
           Will attempt to try and get the instance of rottnest that is
           initialised
           If it is not initialised, it will return None
           If it is initialised, it will return RottnestApplication 
        '''
        instance = RottnestApplication._appinstance
        if instance is None:
            return None
        else:
            return instance
            
    
    @staticmethod
    def get_uninitialised_instance():
        '''
           Do note, this mechanism is only for testing and mock devices
           that are to provide some level of introspection within the system
           itself
        '''
        print("UNIT")
        wsock = WebSocket(None, StringIO(''), None) # NOTE: Un-init'd
        wsock_sem = Semaphore()
        return RottnestApplication(wsock, wsock_sem, is_uninit=True)

    @classmethod
    def get_instance(cls):
        '''
            Retrieves a singleton instance from this object
            Will throw an exception if the object has not been instantiated before
        '''
        if cls._appinstance is None:
            raise RottnestApplicationUnavailableException()
        else:
            return cls._appinstance

    

    def websocket_stream_write(self, stream):
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
            self.wsock.send(Rottnest\
                       .start_packet(Rottnest.data.run_result)\
                       .set_payload(stream_data)\
                       .build())

    def websocket_result_write(self, results):
        '''
            Writes data to the websocket via the rottnest instance
            On results from composer objects    
            NOTE: Better rename or generalise this method
        '''
        
        self.wsock.send(Rottnest\
                       .start_packet(Rottnest.data.run_result)\
                       .set_payload(results)\
                       .build())


    def websocket_result_final_write(self, results):
        '''
            Writes data to the websocket via the rottnest instance
            On results from composer objects    
            NOTE: Better rename or generalise this method
        '''
        
        self.wsock.send(Rottnest\
                       .start_packet(Rottnest.data.run_result)\
                       .set_payload(results)\
                       .put("cu_id", "TOTAL") \
                       .build())
        

    def websocket_heartbeat(self):
        '''
           Provides a heartbeat mechanism for the websocket
           to ensure that it is kept alive
        '''
        heartbeat_package = Rottnest.make_message(Rottnest.liveness)
        wsock = self.wsock
        wsock.send(heartbeat_package)

    def get_websocket(self):
        '''
            Gets the websocket that is attached to the application
        '''
        return self.wsock

    def set_wsock(self, wsock):
        '''
           Sets the websocket connection 
        '''
        self.wsock = wsock

    def set_wsock_and_sem(self, wsock, wsem):
        '''
           Sets the websocket and semaphore 
        '''
        self.wsock = wsock
        self.wsock_sem = wsem

    def get_responder_ref(self):
        exts = self.get_extensions()
        if exts.get_responder_ref is not None:
            return exts.get_responder_ref()
        else:
            return None

    def get_extensions(self):
        '''
           Gets object that was extended by the loaders 
        '''
        return self.app_extensions

    def setv(self, key, value):
        """
            Sets a value using with the key supplied  
        """
        self.app_state_map[key] = value

    def getv(self, key):
        """
            Gets a value using the key, if the value
            does not exist that is mapped to the key, None
            is returned
        """
        v = None
        if key in self.app_state_map:
            v = self.app_state_map[key]
        return v

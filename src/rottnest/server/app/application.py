"""
    Rottnest application class
"""
from rottnest.server.app.app_config import ApplicationConfig, AppExtensions
from rottnest.debug.monitor import DebugMonitor
from rottnest.server.websocket.websocket_proxy import RottnestWebSocketProxy

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
            websocket_proxy: RottnestWebSocketProxy | None,
            apploader=ApplicationConfig.default(),
            is_uninit=False,
            reload=True
        ):
        """
            Initialises an application
            with simple dictionary that will
            map arbitrary objects
            ApplicationConfig will load defaults or
            what is specified
        """
        self.websocket_proxy = websocket_proxy
        self.app_loader_ref = apploader
        self.is_uninit = is_uninit
        self.app_state_map = {}
        self.app_extensions = AppExtensions()
        if reload:
            apploader.load_and_attach(self.app_extensions)
        DebugMonitor.current().set_console_context(self)
        DebugMonitor.current().get_console().set_app(self)

        if RottnestApplication._appinstance is None \
            or RottnestApplication._appinstance.is_uninit:
            RottnestApplication._appinstance = self


    def reload_extensions(self):
        '''
           Reload the plugins as necessary 
        '''
        self.app_loader_ref.load_and_attach(self.app_extensions)



    @classmethod
    def try_get_instance(cls, reload=True):
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
        return RottnestApplication(websocket_proxy=None, is_uninit=True)

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


    def get_websocket(self):
        '''
            Gets the websocket that is attached to the application
        '''
        return self.websocket_proxy.websocket if self.websocket_proxy \
            is not None else None

    def get_websocket_proxy(self):
        '''
             Gets the websocket proxy that is attached to the application
        '''
        return self.websocket_proxy

    def set_websocket_proxy(self, websocket_proxy):
        '''
          Sets the websocket proxy  
        '''
        self.websocket_proxy = websocket_proxy

    def set_wsock(self, wsock):
        '''
           Sets the websocket connection 
        '''
        self.wsock = wsock

    def set_wsock_and_sem(self, wsock, wsem):
        '''
           Sets the websocket and semaphore
           - This is now a wrapper method to eliminate issues
        '''
        self.set_websocket_proxy_from_websocket(wsock, wsem)

    def set_websocket_proxy_from_websocket(self, wsock, semaphore):
        '''
           Constructs a websocket proxy from a websocket and semaphore given 
        '''
        self.websocket_proxy = RottnestWebSocketProxy(wsock, semaphore)

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

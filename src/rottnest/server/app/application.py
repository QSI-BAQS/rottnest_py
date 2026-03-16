"""
    Rottnest application class
"""
from rottnest.server.app.app_config import ApplicationConfig, AppExtensions
from rottnest.debug.monitor import DebugMonitor

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
            apploader=ApplicationConfig.default()
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
        self.app_state_map = {}
        self.app_extensions = AppExtensions()
        apploader.load_and_attach(self.app_extensions)
        DebugMonitor.current().set_console_context(self)
        DebugMonitor.current().get_console().set_app(self)

        if RottnestApplication._appinstance is None:
            RottnestApplication._appinstance = self
        
        

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
        return self.wsock

    def set_wsock(self, wsock):
        '''
           Sets the websocket connection 
        '''
        self.wsock = wsock

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

"""
    Rottnest application class
"""

from rottnest.server.app.app_config import ApplicationConfig, AppExtensions
from rottnest.debug.monitor import DebugMonitor

class RottnestApplication:
    """
        Application class
        Acts as a simple map 
        To have more concrete information provided later
    """
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
        DebugMonitor.current().get_console().set_app(self)

    def set_wsock(self, wsock):
        '''
           Sets the websocket connection 
        '''
        self.wsock = wsock

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

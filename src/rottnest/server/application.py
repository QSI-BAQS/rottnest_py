


class RottApplication:
    """
        Application class that will can be used
        as a simple map right now.

        To have more concrete information provided later
    """
    def __init__(self, wsock, wsock_sem):
        """
            Initialises an application
            with simple dictionary that will
            map arbitrary objects
        """
        self.wsock = wsock
        self.wsock_sem = wsock_sem
        self.app_state_map = {}

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

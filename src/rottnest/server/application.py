from rottnest.plugin.arch_config import ArchRegistryConfig
from rottnest.plugin.arch_plugin import ArchPluginRegistry


class RottApplication:
    """
        Application class that will can be used
        as a simple map right now.

        To have more concrete information provided later
    """
    def __init__(self, wsock, wsock_sem, arch_config=None):
        """
            Initialises an application
            with simple dictionary that will
            map arbitrary objects

            This will also load architectures as outlined by a config
            and manage a registry for them
        """
        self.wsock = wsock
        self.wsock_sem = wsock_sem
        if arch_config is None:
            self.arch_registry = ArchPluginRegistry()
        else:
            self.arch_registry = ArchRegistryConfig.load_config(arch_config).to_plugin_registry()

        self.app_state_map = {}

    

    def get_arch_registry(self):
        """
           Retrieves the architecture registry 
        """
        return self.arch_registry

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

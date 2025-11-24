'''
    Manages loading of architectures
'''
from ..config import architectures_file_name

from .plugin_manager import PluginManager

ROTTNEST_ARCHITECTURE_MODULE_TAG = 'rottnest_architectures'

class ArchitecturePlugins(PluginManager):
    '''
       Architecture Plugin manager
    '''
    _config_file_name = architectures_file_name

    def __init__(self, modules=None, config_path=None):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin
        '''

        if modules is None:
            modules = tuple()

        # Load from config
        super().__init__(
            module_tag = ROTTNEST_ARCHITECTURE_MODULE_TAG,
            modules = modules,
            config_path=config_path
        )

    @staticmethod
    def load_config_or_default(path: str):
        '''
           This has been re-introduced as it is useful for sensible
           default to be included to ensure loading
        '''
        plugins = ArchitecturePlugins(config_path=path)
        return plugins

    def get_current_architecture(self):
        '''
            Getter for the current architecture
        '''
        return self._current_option

    def get_architectures(self):
        '''
            Getter for architecture objects
        '''
        return self._options

    def set_current_architecture(self, key):
        '''
            Setter method for the current architecture
            Treats this class as the sole interface for
            passing architecture information to the
            front end
        '''
        self._set_current_option(key)

    def _force_set_current_architecture(self, architecture):
        '''
            Forcible setter for the current architecture
            Used to set non-displaying architectures
            Such as the pre-processor
        '''
        self._current_option = architecture

    def get_architecture_names(self):
        '''
           Retrieves a list of dtos of the architectures
           that the front-end can select from.
        '''
        return list(self._options.keys())

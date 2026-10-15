'''
    Manages loading of architectures
'''

import rottnest_preprocessor

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

        # Preprocessor achitecture is a default in rottnest
        if modules is None:
            modules = [rottnest_preprocessor]
        else:
            modules = [rottnest_preprocessor] + modules

        # Load from config
        super().__init__(
            module_tag=ROTTNEST_ARCHITECTURE_MODULE_TAG,
            modules=modules,
            config_path=config_path
        )

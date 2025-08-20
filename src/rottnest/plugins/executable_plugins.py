'''
    Manages loading of executables
'''
from ..config import executables_file_name
from ..executables.executable import ROTTNEST_EXECUTABLE_MODULE_TAG

from .plugin_manager import PluginManager


class ExecutablePlugins(PluginManager):
    '''
       Executable Plugin manager
    '''
    _config_file_name = executables_file_name

    def __init__(self, modules=None, config_path=None):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin
        '''

        if modules is None:
            modules = tuple()

        # Load from config
        super().__init__(
            module_tag = ROTTNEST_EXECUTABLE_MODULE_TAG,
            modules = modules,
            config_path = config_path
        )

    def get_current_executable(self):
        '''
            Getter for the current executable
        '''
        return self._current_option

    def get_executables(self):
        '''
            Getter for executable objects
        '''
        return self._options

    def set_current_executable(self, key):
        '''
            Setter method for the current executable
            Treats this class as the sole interface for
            passing executable information to the
            front end
        '''
        self._set_current_option(key)

    def get_executable_names(self):
        '''
           Retrieves a list of dtos of the executables
           that the front-end can select from.
        '''
        return list(self._options.keys())

        #for k, v in self.:
        #    dtos.append(
        #             'arch_name': name,
        #     })
        #return dtos

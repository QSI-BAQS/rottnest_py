'''
    Manages loading of executables
'''
import rottnest_qasm_executables

from rottnest.config import executables_file_name
from rottnest.executables.executable import (
    ROTTNEST_EXECUTABLE_MODULE_TAG,
    RottnestExecutable
)

from .plugin_manager import PluginManager


class ExecutablePlugins(PluginManager):
    '''
       Executable Plugin manager
    '''
    _config_file_name = executables_file_name

    def __init__(self, modules=None, config_path=None):
        '''
           Creates a new Plugin that can be used by
           rottnest, this manager that will hold objects
           that represent executables usable within the system
        '''

        if modules is None:
            modules = [rottnest_qasm_executables]
        else:
            modules = [rottnest_qasm_executables] + modules

        # Load from config
        super().__init__(
            plugin_tag=ROTTNEST_EXECUTABLE_MODULE_TAG,
            modules=modules,
            config_path=config_path
        )



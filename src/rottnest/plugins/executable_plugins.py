'''
    Manages loading of executables
'''
from rottnest.rz_decomposer import DEFAULT_PRECISION

from ..config import executables_file_name
from ..executables.executable import (
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
            modules = []

        # Load from config
        super().__init__(
            module_tag=ROTTNEST_EXECUTABLE_MODULE_TAG,
            modules=modules,
            config_path=config_path
        )

    @staticmethod
    def from_config_or_default(path) -> 'ExecutablePlugins':
        '''
           Loading config or default, gets the executable plugins instance
        '''
        modules = []
        plugins = ExecutablePlugins(modules=modules, config_path=path)

        return plugins

    @staticmethod
    def with_modules(modules: list[str]) -> 'ExecutablePlugins':
        '''
           Loadable variant which just expects modules to be
           push into it
        '''
        plugins = ExecutablePlugins(modules=modules, config_path=None)

        return plugins

    def get_executable_params(self):
        '''
            Parameters for executable
        '''
        return self.get_parameters()

    def get_precision(self):
        '''
            Gets the precision
        '''
        return self.get_parameters().get(
            RottnestExecutable.RZ_PREC,
            DEFAULT_PRECISION
        )

    def set_executable_params(self, **params) -> None:
        '''
           Sets executable parameters
        '''
        self.set_parameters(params)

    def set_executable_params_from_dict(self, params: dict) -> None:
        '''
           Sets executable parameters
           This method only exists to skip unpacking and repacking
        '''
        self.set_parameters(params)

    def __process_default_params(self, params: dict) -> dict:
        '''
            Strips type information from default param dicts
        '''
        stripped_params = {}
        for key, val in params.items():
            _type_info, value = val
            stripped_params[key] = value

        return stripped_params

    def get_current_executable(self) -> RottnestExecutable | None:
        '''
            Getter for the current executable
        '''
        if self._current_option is None:
            return None
        return self._current_option(**self.get_executable_params())

    def get_executables(self) -> dict:
        '''
            Getter for executable objects
        '''
        return self._options

    def set_current_executable(self, key) -> bool:
        '''
            Setter method for the current executable
            Treats this class as the sole interface for
            passing executable information to the
            front end

            If the current option is not selected, it should return `False`
            for the caller
        '''
        self._set_current_option(key)
        if self._current_option is not None:
            current_option: RottnestExecutable = self._current_option

            # Sets default params
            self.set_executable_params_from_dict(
                self.__process_default_params(
                    current_option.get_parameters()
                )
            )
            return True
        return False

    def get_executable_names(self) -> list[str]:
        '''
           Retrieves a list of dtos of the executables
           that the front-end can select from.
        '''
        return list(self._options.keys())

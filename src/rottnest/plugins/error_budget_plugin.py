'''
    Manages loading of error budget modules
'''

import rottnest_error_budgets

from ..config import error_budgets_file_name
from .plugin_manager import PluginManager

ROTTNEST_ERROR_BUDGET_MODULE_TAG = 'rottnest_error_budgets'


class ErrorBudgetPlugins(PluginManager):
    '''
       Error Budget Plugin manager
    '''
    _config_file_name = error_budgets_file_name

    def __init__(self, modules=None, config_path=None):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin
        '''

        # Preprocessor achitecture is a default in rottnest
        if modules is None:
            modules = [rottnest_error_budgets]
        else:
            modules = [rottnest_error_budgets] + modules

        # Load from config
        super().__init__(
            module_tag=ROTTNEST_ERROR_BUDGET_MODULE_TAG,
            modules=modules,
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

    def get_current_error_budget_model(self):
        '''
            Getter for the current architecture
        '''
        return self._current_option

    def get_error_budget_models(self):
        '''
            Getter for architecture objects
        '''
        return self._options

    def set_current_error_budget_model(self, key):
        '''
            Setter method for the current architecture
            Treats this class as the sole interface for
            passing architecture information to the
            front end
        '''
        self._set_current_option(key)

    def get_error_budget_names(self):
        '''
           Retrieves a list of dtos of the architectures
           that the front-end can select from.
        '''
        return list(self._options.keys())

    def get_error_budget_params(self):
        '''
           Gets the architecture parameters
        '''
        return self.get_parameters()

    def set_error_budget_params(self, **params) -> None:
        '''
           Sets the new parameters and updates the
           architecture information
        '''
        self.set_parameters(params)

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

        # Default error budget module
        if modules is None:
            modules = [rottnest_error_budgets]
        else:
            modules = [rottnest_error_budgets] + modules

        # Load from config
        super().__init__(
            plugin_tag=ROTTNEST_ERROR_BUDGET_MODULE_TAG,
            modules=modules,
            config_path=config_path
        )

    def get_current_option(self) -> "Option":
        '''
            Gets the currently set option
            Runs the constructor with params
        '''
        option = super().get_current_option()
        # Temporary fix for a default
        # TODO: Remove when front end support for error budgets is integrated
        if option is None:
            from rottnest_error_budgets import EvenDistribution          
            self.set_current_option(EvenDistribution.get_name())

        return super().get_current_option()

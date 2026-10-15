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
            module_tag=ROTTNEST_ERROR_BUDGET_MODULE_TAG,
            modules=modules,
            config_path=config_path
        )

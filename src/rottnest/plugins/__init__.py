'''
    Plugin manager system
'''

from .architecture_plugins import ArchitecturePlugins
from .executable_plugins import ExecutablePlugins
from .error_budget_plugins import ErrorBudgetPlugins


executables = ExecutablePlugins.default_loader()
architectures = ArchitecturePlugins.default_loader()
error_budgets = ErrorBudgetPlugins.default_loader()


plugin_managers = [architectures, executables, error_budgets]

_from_tag = {
    manager.get_plugin_tag()
    for manager in plugin_managers 
}

def get_manager_from_tag(tag: str) -> "PluginManager":
    '''
        Getter mapping strings to plugin manager
        Used to genericise calls to the interface over IPC 
    '''
    global _from_tag
    return _from_tag.get(tag, None)

def get_module_keys() -> dict:
    '''
        Gets strings by module tag
    '''
    return {
        manager.get_plugin_tag():
        manager.get_synchronisation_strings()
        for manager in plugin_managers
    }

def override_architectures(architectures_override: ArchitecturePlugins):
    '''
       Allows for overriding the architecture plugins 
    '''
    global architectures
    architectures = architectures_override

def override_executables(executables_override: ExecutablePlugins):
    '''
       Allows for overriding the architecture plugins 
    '''
    global executables
    executables = executables_override

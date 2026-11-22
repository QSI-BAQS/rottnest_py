'''
    Endpoint functions for the priority process
    These are thin layers that can be overridden later as needed
'''
from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure
from rottnest.procedures.option_setters import procedure_set_option, procedure_load_modules
from rottnest.procedures.option_setters.layout_setters import SynchroniseLayoutsProcedure
from rottnest.procedures.option_setters.procedure_load_modules import LoadModulesProcedure

from rottnest.plugins import architectures, executables

from . import commands
from .callgraph import CallGraph
from .visualiser import Visualiser


# Simple state wrapper for visualiser reloads
def reload_visualiser(fn):
    def _wrap(*args, **kwargs):
        res = fn(*args, **kwargs)
        Visualiser.setup_worker()
        return res
    return _wrap

def reload_callgraph(fn):
    def _wrap(*args, **kwargs):
        CallGraph.reset()
        res = fn(*args, **kwargs)
        return res
    return _wrap


def synchronise_modules(module_keys: dict):
    '''
        Synchronises the modules
    '''
    LoadModulesProcedure(module_keys).execute()

@reload_callgraph
@reload_visualiser
def set_options(options_setter: dict):
    '''
        Sets plugin options
    '''
    for plugin_tag, (option_key, parameters) in option_setter.items():
        procedure_set_option.SetOptionProcedure(
            plugin_tag,
            option_key,
            parameters
        ).execute()

        # Reload visualiser
        if plugin_tag == architectures.get_plugin_tag():
             Visualiser.setup_worker()

        if plugin_tag == executables.get_plugin_tag():
            DecompositionPatchProcedure().execute()

@reload_callgraph
def set_option(plugin_tag, option_key, parameters):
    '''
        Sets an option
    '''
    procedure_set_option.SetOptionProcedure(
        plugin_tag,
        option_key,
        parameters
    ).execute()

    # Reload visualiser
    if plugin_tag == architectures.get_plugin_tag():
         Visualiser.setup_worker()

    if plugin_tag == executables.get_plugin_tag():
        DecompositionPatchProcedure().execute()

@reload_callgraph
def synchronise_layouts(layouts:dict):
    '''
        Synchronises layouts
    '''
    SynchroniseLayoutsProcedure(layouts).execute()
    return

def get_callgraph(graph_id: str) -> list:
    '''
        Gets objects from the callgraph
        Returned object
    '''
    return CallGraph.get_graph(graph_id=graph_id)

def get_visualiser(graph_id: str):
    '''
        Compiles object to visualiser
    '''
    parser = CallGraph.get_visualiser_parser(graph_id)
    Visualiser.build_compute_units(parser)
    return Visualiser.next()

def next_visualiser():
    '''
        Gets next visualiser object in sequence
    '''
    return Visualiser.next()

priority_worker_tasks = {
    commands.SET_OPTION: set_option,
    commands.SYNCHRONISE_MODULES: synchronise_modules,
    commands.SYNCHRONISE_LAYOUTS: synchronise_layouts,
    commands.GET_CALLGRAPH: get_callgraph,
    commands.GET_VISUALISER: get_visualiser
}

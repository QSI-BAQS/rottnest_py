'''
    Endpoint functions for the priority process
    These are thin layers that can be overridden later as needed
'''
from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure
from rottnest.procedures.option_setters.project_setters import SynchroniseModulesProcedure, SetArchitectureProcedure, SetExecutableProcedure  
from rottnest.procedures.option_setters.layout_setters import SynchroniseLayoutsProcedure

from . import commands
from .callgraph import CallGraph

def synchronise_modules(architectures, executables):
    '''
        Synchronises the modules
    '''
    SynchroniseModulesProcedure(architectures, executables).execute()
    return

def synchronise_layouts(layouts:dict):
    '''
        Synchronises layouts
    '''
    SynchroniseLayoutsProcedure(layouts)
    return
    
def set_architecture(architecture: str):
    '''
        Sets the architecture
    '''
    SetArchitectureProcedure(architecture).execute()
    return

def set_executable(executable: str):
    '''
        Sets the executable
    '''
    SetExecutableProcedure(executable).execute()
    # Call the decomposition immediately to hook everything
    DecompositionPatchProcedure().execute()
    return

def set_executable_params(params):
    '''
        Sets the executable parameters
    '''
    SetExecutableParametersProcedure(params).execute()
    return

def get_callgraph(graph_id: str) -> list:
    '''
        Gets objects from the callgraph
        Returned object
    '''
    return CallGraph.get(graph_id=graph_id)

priority_worker_tasks = {
    commands.SYNCHRONISE_MODULES: synchronise_modules,
    commands.SYNCHRONISE_LAYOUTS: synchronise_layouts,
    commands.SET_ARCHITECTURE: set_architecture,
    commands.SET_EXECUTABLE: set_executable,
    commands.SET_EXECUTABLE_PARAMS: set_executable_params,
    commands.GET_CALLGRAPH: get_callgraph
}

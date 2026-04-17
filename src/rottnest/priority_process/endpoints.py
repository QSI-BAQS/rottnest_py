'''
    Endpoint functions for the priority process
    These are thin layers that can be overridden later as needed
'''
from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure
from rottnest.procedures.option_setters.project_setters import SynchroniseModulesProcedure, SetArchitectureProcedure, SetExecutableProcedure  
from rottnest.procedures.option_setters.layout_setters import SynchroniseLayoutsProcedure

from . import commands
from .callgraph import CallGraph
from .visualiser import Visualiser

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
    Visualiser.setup_worker()
    return
    
def set_architecture(architecture: str):
    '''
        Sets the architecture
    '''
    SetArchitectureProcedure(architecture, pool=False).execute()
    Visualiser.setup_worker()
    return

def set_executable(executable: str):
    '''
        Sets the executable
    '''
    SetExecutableProcedure(executable, params=None, pool=False).execute()
    # Call the decomposition immediately to hook everything
    DecompositionPatchProcedure().execute()
    CallGraph.flush_caches()
    return

def set_executable_params(params):
    '''
        Sets the executable parameters
    '''
    SetExecutableParametersProcedure(params).execute()
    CallGraph.flush_caches()

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
    commands.SYNCHRONISE_MODULES: synchronise_modules,
    commands.SYNCHRONISE_LAYOUTS: synchronise_layouts,
    commands.SET_ARCHITECTURE: set_architecture,
    commands.SET_EXECUTABLE: set_executable,
    commands.SET_EXECUTABLE_PARAMS: set_executable_params,
    commands.GET_CALLGRAPH: get_callgraph,
    commands.GET_VISUALISER: get_visualiser
}

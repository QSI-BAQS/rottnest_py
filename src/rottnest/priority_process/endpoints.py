'''
    Endpoint functions for the priority process
    These are thin layers that can be overridden later as needed
'''
from rottnest.procedures.option_setters.project_setters import SynchroniseModulesProcedure, SetArchitectureProcedure, SetExecutableProcedure  

from . import commands


def synchronise_modules(architectures, executables):
    '''
        Synchronises the modules
    '''
    SynchroniseModulesProcedure(architectures, executables).execute()
    
def set_architecture(architecture: str):
    '''
        Sets the architecture
    '''
    SetArchitectureProcedure(architecture).execute()

def set_executable(executable: str):
    '''
        Sets the executable
    '''
    SetExecutableProcedure(executable).execute()

def set_executable_params(params):
    '''
        Sets the executable parameters
    '''
    SetExecutableParametersProcedure(params).execute()

priority_worker_tasks = {
    commands.SYNCHRONISE_MODULES: synchronise_modules,
    commands.SET_ARCHITECTURE: set_architecture,
    commands.SET_EXECUTABLE: set_executable,
    commands.SET_EXECUTABLE_PARAMS: set_executable_params
}




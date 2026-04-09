'''
    Model functions for the rottnest server interface
    These functions bind the executable singleton instance methods
    to the controller's caller methods
'''

from rottnest.plugins import executables as singleton
from rottnest.server.util.result import Result

def get_executables() -> tuple[dict, list]:
    '''
        Returns executables from the singleton instance
    '''
    return (get_current_executable(), singleton.get_executable_names())


def get_current_executable() -> dict:
    '''
        Returns the currently loaded executable from the singleton
        instance
    '''
    exec_data = singleton.get_current_executable()
    # kv[0]    - Name
    # kv[1][0] - Type
    # kv[1][1] - Argument 
    exec_params = list(map(lambda kv: [kv[0], kv[1][0].__name__, kv[1][1]],\
                           exec_data.get_parameters().items()))
    exec_dict = {
        "name": exec_data.get_name(),
        "parameters": exec_params
    }
    return exec_dict


# BUG: Apparently this is not being set correctly?
def set_current_executable(name: str) -> Result:
    '''
        It sets the executable using a string name
        
        Returns the currently loaded executable from the singleton
        instance
    '''
    # TODO: Bug here in the set_current_executable
    # BUG: Need to fix ASAP!
    return singleton.set_current_executable(name)


def get_current_params() -> Result:
    '''
        Gets the parameters for the current executable
    '''
    return singleton.get_executable_params()


def set_current_params(params: dict) -> Result:
    '''
        Sets the executable parameters
    '''
    # Process parameters and omit type from tuple
    params_reduction = {}
    for (pname, ptuple) in params.items():

        params_reduction[pname] = ptuple[1]
    
    singleton.set_executable_params(**params_reduction)
    return get_current_params()

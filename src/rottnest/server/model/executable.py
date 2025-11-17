'''
    Model functions for the rottnest server interface
    These functions bind the executable singleton instance methods
    to the controller's caller methods
'''

from rottnest.plugins import executables as singleton
from rottnest.server.responder import Result

def get_executables() -> Result:
    '''
        Returns executables from the singleton instance
    '''
    return singleton.get_executables()


def get_current_executable() -> Result:
    '''
       Returns the currently loaded executable from the singleton
        instance
    '''
    return singleton.get_current_executable()


def set_current_executable(params: dict) -> Result:
    '''
       Returns the currently loaded executable from the singleton
        instance
    '''
    return singleton.get_current_executable(**params)


def get_current_config() -> Result:
    '''
        Gets the parameters for the current executable
    '''
    return singleton.get_executable_params()


def set_current_config(params: dict) -> Result:
    '''
        Sets the executable parameters
    '''
    singleton.set_executable_params(**params)

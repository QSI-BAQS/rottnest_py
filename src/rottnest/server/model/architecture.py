'''
    Model functions for the rottnest server interface
    These functions bind the executable singleton instance methods
    to the controller's caller methods
'''

from rottnest.plugins import architectures as singleton 
from rottnest.server.util.result import Result

def get_architecture_list() -> list:
    '''
        Returns architectures from the singleton instance
    '''
    return singleton.get_architectures()


def get_current_architecture() -> str:
    '''
       Returns the currently loaded architecture from the singleton
        instance
    '''
    return singleton.get_current_architecture()


def set_current_architecture(arch: str) -> Result:
    '''
       Returns the currently loaded architecture from the singleton
        instance
    '''
    return singleton.set_current_architecture(arch)


def get_current_config() -> dict:
    '''
        Gets the parameters for the current architecture
    '''
    return singleton.get_architecture_params()


def set_current_config(params: dict):
    '''
        Sets the architecture parameters
    '''
    singleton.set_architecture_params(**params)

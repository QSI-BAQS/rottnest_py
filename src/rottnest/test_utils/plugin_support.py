'''
    Unsafe helper functions for testing plugins
'''
from ..plugins import architectures, executables

def force_add_option(obj, key, value):
    '''
        Unsafe internal access function
    '''
    obj._options[key] = value

def add_executable(key, executable):
    '''
        Test helper function to add an executable
    '''
    force_add_option(executables, key, executable)

def add_architecture(key, architecture):
    '''
        Test helper function to add an architecture
    '''
    force_add_option(architectures, key, architecture)

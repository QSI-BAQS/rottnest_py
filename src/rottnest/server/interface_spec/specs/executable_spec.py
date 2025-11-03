'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification

# Symbols
GET_EXECUTABLE_LIST = 'executable.get_list'
GET_EXECUTABLE_CURRENT = 'executable.get_current'
SET_EXECUTABLE_CURRENT = 'executable.set_current'
GET_EXECUTABLE_CONFIG = 'executable.get_config'
SET_EXECUTABLE_CONFIG = 'executable.set_config'

# Routes
executable_routes = [
    GET_EXECUTABLE_LIST,
    GET_EXECUTABLE_CURRENT,
    SET_EXECUTABLE_CURRENT,
    GET_EXECUTABLE_CONFIG,
    SET_EXECUTABLE_CONFIG
]

class ExecutableSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = executable_routes 

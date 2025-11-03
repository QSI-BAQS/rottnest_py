'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification

# Symbols
EXECUTABLE_LIST_GET = 'executable.get_list'
EXECUTABLE_CURRENT_GET = 'executable.get_current'
EXECUTABLE_CURRENT_SET = 'executable.set_current'
EXECUTABLE_CONFIG_GET = 'executable.get_config'
EXECUTABLE_CONFIG_SET = 'executable.set_config'

# Routes
executable_routes = [
    EXECUTABLE_LIST_GET,
    EXECUTABLE_CURRENT_GET,
    EXECUTABLE_CURRENT_SET,
    EXECUTABLE_CONFIG_GET,
    EXECUTABLE_CONFIG_SET
]

class ExecutableSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = executable_routes 

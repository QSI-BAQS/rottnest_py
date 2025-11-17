'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'executable'

# Symbols
GET_EXECUTABLE_LIST = 'get_list'
GET_EXECUTABLE_CURRENT = 'get_current'
SET_EXECUTABLE_CURRENT = 'set_current'
GET_EXECUTABLE_CONFIG = 'get_config'
SET_EXECUTABLE_CONFIG = 'set_config'

# Routes
_executable_routes = [
    GET_EXECUTABLE_LIST,
    GET_EXECUTABLE_CURRENT,
    SET_EXECUTABLE_CURRENT,
    GET_EXECUTABLE_CONFIG,
    SET_EXECUTABLE_CONFIG
]

executable_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _executable_routes]

class ExecutableSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = executable_routes 
    _module_prefix = MODULE_PREFIX

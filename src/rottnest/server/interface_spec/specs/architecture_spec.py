'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'arch'

# Symbols
GET_ARCHITECTURE_LIST = 'get_list'
GET_CURRENT_ARCHITECTURE = 'get_current'
SET_CURRENT_ARCHITECTURE = 'set_current'
GET_ARCHITECTURE_CONFIG = 'get_config'
SET_ARCHITECTURE_CONFIG = 'set_config'

# Routes
_architecture_routes = [
    GET_ARCHITECTURE_LIST,
    GET_CURRENT_ARCHITECTURE,
    SET_CURRENT_ARCHITECTURE,
    GET_ARCHITECTURE_CONFIG,
    SET_ARCHITECTURE_CONFIG
]

architecture_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _architecture_routes]


class ArchitectureSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = architecture_routes 
    _module_prefix = MODULE_PREFIX 

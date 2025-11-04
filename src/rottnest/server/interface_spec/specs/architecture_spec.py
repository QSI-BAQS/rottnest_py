'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification

# Symbols
GET_ARCHITECTURE_LIST = 'arch_list'
GET_CURRENT_ARCHITECTURE = 'arch_get'
SET_CURRENT_ARCHITECTURE = 'arch_set'
GET_ARCHITECTURE_CONFIG = 'arch_get_config'
SET_ARCHITECTURE_CONFIG = 'arch_set_config'

# Routes
architecture_routes = [
    GET_ARCHITECTURE_LIST,
    GET_CURRENT_ARCHITECTURE,
    SET_CURRENT_ARCHITECTURE,
    GET_ARCHITECTURE_CONFIG,
    SET_ARCHITECTURE_CONFIG
]

class ArchitectureSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = architecture_routes 

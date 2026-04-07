'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'procedure'

# Symbols
EXECUTE_PROCEDURE_IMMEDIATE = 'run_immediate'
EXECUTE_PROCEDURE_DEFER = 'run_defer'
GET_PROCEDURE_STATE = 'get_state'


# Routes
_procedure_routes = [
    EXECUTE_PROCEDURE_IMMEDIATE,
    EXECUTE_PROCEDURE_DEFER,
    GET_PROCEDURE_STATE,
]

procedure_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _procedure_routes]

class ProcedureSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = procedure_routes
    _module_prefix = MODULE_PREFIX

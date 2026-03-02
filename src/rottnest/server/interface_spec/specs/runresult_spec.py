
'''
    Specification for the ComputeUnit API endpoints
'''

from rottnest.server.interface_spec.interface_spec \
    import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'callgraph'

# Symbols
POLL_CU_STATUS = "cu_status"
QUERY_CU_RESULT_DATA = "cu_query_result"
QUERY_CU_RESULT_BUFFER = "cu_query_buffer"
QUERY_CU_RESULT_EXEC = "cu_query_execution"
QUERY_CU_RESULT_VOL_SEGMENT = "cu_query_"

# Routes
_callgraph_routes = [
]

callgraph_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _callgraph_routes]


class CallGraphSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = callgraph_routes
    _module_prefix = MODULE_PREFIX

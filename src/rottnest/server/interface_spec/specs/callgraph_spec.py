'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'callgraph'

# Symbols
GET_ROOT_GRAPH = 'get_root_graph'
GET_GRAPH = 'get_graph'
GET_STATUS = 'get_status'
RUN_GRAPH_NODE = 'run_graph_node'

# Routes
_callgraph_routes = [
    GET_ROOT_GRAPH,
    GET_GRAPH,
    GET_STATUS,
    RUN_GRAPH_NODE
]

callgraph_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _callgraph_routes]


class CallGraphSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = callgraph_routes
    _module_prefix = MODULE_PREFIX

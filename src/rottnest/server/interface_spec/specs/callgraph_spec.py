'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification

# Symbols
GET_ROOT_GRAPH = 'GET_ROOT_GRAPH'
GET_GRAPH = 'GET_GRAPH'
GET_STATUS = 'GET_STATUS'
RUN_GRAPH_NODE = 'RUN_GRAPH_NODE'

# Routes
callgraph_routes = [
    GET_ROOT_GRAPH,
    GET_GRAPH,
    GET_STATUS,
    RUN_GRAPH_NODE
]

class CallGraphSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = callgraph_routes

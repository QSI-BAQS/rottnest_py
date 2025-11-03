'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification

# Symbols
USE_LAYOUT = 'layout_use'

# Routes
layout_routes = [
    USE_LAYOUT
]

class LayoutSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = layout_routes 

'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification

# Symbols
SET_LAYOUT = 'layout_use'

# Routes
layout_routes = [
    SET_LAYOUT
]

class LayoutSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = layout_routes 

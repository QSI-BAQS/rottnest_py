'''
    Specification for the callgraph API endpoints
'''

from rottnest.server.interface_spec.interface_spec import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'layout'

# Symbols
RUN_LAYOUT = 'run_layout'
SET_LAYOUT = 'set_layout'


# Routes
_layout_routes = [
    SET_LAYOUT,
    RUN_LAYOUT
]

layout_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _layout_routes]

class LayoutSpecification(RouteInterfaceSpecification):
    '''
        Specification of the callgraph
    '''
    _routes = layout_routes 
    _module_prefix = MODULE_PREFIX

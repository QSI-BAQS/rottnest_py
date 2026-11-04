'''
    Specification for the ComputeUnit API endpoints
'''

from rottnest.server.interface_spec.interface_spec \
    import RouteInterfaceSpecification, ROTTNEST_PREFIX

MODULE_PREFIX = 'postprocessing'

# Symbols
POSTPROCESSING_SET_FIELDS = "set_fields"
POSTPROCESSING_GET_FIELDS = "get_fields"
POSTPROCESSING_EVALUATE   = "evaluate"

_postprocessing_routes = [
    POSTPROCESSING_SET_FIELDS,
    POSTPROCESSING_GET_FIELDS,
    POSTPROCESSING_EVALUATE
]

postprocessing_routes = [f"{ROTTNEST_PREFIX}.{MODULE_PREFIX}.{route}" for route in _postprocessing_routes]

class PostProcessingSpecification(RouteInterfaceSpecification):
    '''
        Specification of the postprocessing
    '''
    _routes = postprocessing_routes
    _module_prefix = MODULE_PREFIX

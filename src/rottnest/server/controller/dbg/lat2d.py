from rottnest.region_builder import json_to_region
from rottnest.server.responder import responder

@responder.register('example_arch')
def example_arch(*args, **kwargs):
    """
       Example architecture to help with testing the bindings
       of the application  
    """
    return json_to_region.example

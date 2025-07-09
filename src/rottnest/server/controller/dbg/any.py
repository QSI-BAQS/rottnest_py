from rottnest.server.responder import responder
from rottnest.server.model import architecture
from rottnest.compute_units.architecture_proxy import saved_architectures

@responder.register('debug_send')
def debug_send(app, message, **kwargs):
    # Debug:
    # architecture.run_debug(next(iter(saved_architectures.keys())), wsock)
    # return get_status({'cu_id': 'debug'})
    
    return architecture.run_debug2(next(iter(saved_architectures.keys())))

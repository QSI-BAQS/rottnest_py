from rottnest.server.model import generic_architecture 
from rottnest.server.responder import responder

@responder.register('use')
def use_arch(app, message, **kwargs):
    """
       use_arch, saves using the generic_architecture pathway
       rather than the `architecture`
    """
    arch_json_obj = message['payload']
    return { 'arch_id': generic_architecture.save_arch(arch_json_obj) }

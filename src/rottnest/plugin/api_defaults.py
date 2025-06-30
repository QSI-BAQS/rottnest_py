

from rottnest.server.model import generic_architecture 
from rottnest.server.responder import responder

def identifier_endpoint(name):
    def identifier_endpoint(app, message, **kwargs):
        return { 'identifier': name }
    

#@responder.register('use')
def use_arch(app, message, **kwargs):
    arch_json_obj = message['payload']
    return { 'arch_id': generic_architecture.save_arch(arch_json_obj) }

#@responder.register('status_response')
def get_status(app, message, **kwargs):
    cu_id = message['cu_id']
    return generic_architecture.get_status(cu_id)

@responder.register('get_subtypes')
def get_subtype(app, message, **kwargs):
    return generic_architecture.get_region_subtypes()


@responder.register("run_result")
def run_result(app, message, **kwargs):
    wsock=app.wsock
    wsock_sem=app.wsock_sem
    arch_id = message['payload']['arch_id']
    generic_architecture.run_widget_pool(arch_id, wsock, wsock_sem=wsock_sem)
    return { 'status': 'pending' }


def default_api_map(ident):
    return {
        'identifier': identifier_endpoint(ident)
        'use': use_arch,
        'status_response': get_status,
        'run_result': run_result
    }

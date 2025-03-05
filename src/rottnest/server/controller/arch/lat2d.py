
from rottnest.server.model import architecture 
from rottnest.server.responder import responder

@responder.register('get_router')
def get_router(app, message, **kwargs):
    return architecture.get_router_mapping()

@responder.register('get_args')
def get_args(app, message, **kwargs):
    return architecture.get_region_arguments()

@responder.register('use')
def use_arch(app, message, **kwargs):
    arch_json_obj = message['payload']
    return { 'arch_id': architecture.save_arch(arch_json_obj) }

@responder.register('status_response')
def get_status(app, message, **kwargs):
    cu_id = message['cu_id']
    return architecture.get_status(cu_id)

@responder.register('get_subtypes')
def get_subtype(app, message, **kwargs):
    return architecture.get_region_subtypes()

@responder.register('get_result')
def run_result(app, message, **kwargs):
    #print("Running!", str(message)[:min(200, len(str(message)))])
    wsock = app.wsock
    wsock_sem = app.wsock_sem
    arch_id = message['payload']['arch_id']
    architecture.run_widget_pool(arch_id, wsock, wsock_sem=wsock_sem)
    return { 'status': 'pending' }


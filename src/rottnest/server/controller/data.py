from rottnest.server.model.plugin_architecture import run_widget_pool 
from rottnest.server.responder import responder

@responder.register('run_result')
def run_result(app, message, **kwargs):
    wsock=app.wsock
    wsock_sem=app.wsock_sem
    arch_id = message['payload']['arch_id']
    run_widget_pool(arch_id, wsock, wsock_sem=wsock_sem)
    data = { 'status': 'pending' }
    
    return ('run_result', data)

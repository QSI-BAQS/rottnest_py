from rottnest.server.model.plugin_architecture import run_widget_pool
from rottnest.server.responder import responder


from rottnest.server.interface_spec.route_interface import RouteInterface
from rottnest.server.interface_spec.specs.callgraph_spec import ( 
    MODULE_PREFIX,
    GET_ROOT_GRAPH,
    GET_GRAPH,
    GET_STATUS,
    RUN_GRAPH_NODE
) 
  
from rottnest.server.model import plugin_architecture
from rottnest.server.responder import responder

from rottnest.server.util.result import Result




class RunResultDataInterface(RouteInterface):
    '''
        Interface for run result, it will send out data or it will
        be poll-able to retrieve data from the worker modules
    '''
    _module_prefix = MODULE_PREFIX 



@responder.register('run_result')
def run_result(app, message, **kwargs):
    wsock=app.wsock
    wsock_sem=app.wsock_sem
    arch_id = message['payload']['arch_id']
    #get_root_graph(wsock, wsock_sem)
    run_widget_pool(arch_id, wsock, wsock_sem=wsock_sem)
    data = { 'status': 'pending' }
    
    return ('run_result', data)

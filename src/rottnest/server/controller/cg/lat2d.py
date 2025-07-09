
from rottnest.server.model import architecture 
from rottnest.server.responder import responder, Result

@responder.register('get_root_graph')
def get_root_graph(app, message, **kwargs): 
    wsock = app.wsock
    wsock_sem = app.wsock_sem
    #gobj = message['payload']
    architecture.get_root_graph(wsock, wsock_sem=wsock_sem)
    return Result.Alt('debug', 'get_root_graph pending')


@responder.register('get_graph')
def get_graph(app, message, **kwargs):
    gobj = message['payload']
    
    architecture.cu_executor_pool.get_graph(gobj['gid'])
    graph_object = architecture.cu_executor_pool \
        .manager_priority_completion_queue.get()
    
    return  {
                'gid' : gobj['gid'], #super silly
                'graph_view' : graph_object 
            }


@responder.register('get_status')
def get_status(app, message, **kwargs):
    cu_id = message['cu_id']
    #'message': 'status_response',
    return architecture.get_status(cu_id),


@responder.register("run_graph_node")
def run_graph_node(app, message, **kwargs):
    gid = message['payload']['gid']
    return architecture.run_debug3(gid)



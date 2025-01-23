from bottle import request, abort 
from geventwebsocket import WebSocketError
from rottnest.region_builder import json_to_region
from rottnest.server.model import architecture 
from rottnest.process_pool.process_pool import AsyncIteratorProcessPool

import json

def register_routes(app):
   app.route("/websocket", callback=handle_websocket)

# TODO: Register architecture object
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    # TODO fix which callback
    pool = AsyncIteratorProcessPool(
            websocket_response_callback(wsock,'run_result'))

    try:
        while True:
            # TODO: RPC this whole thing
            try:
                message_raw = wsock.receive()
                if message_raw is None: continue
                print(message_raw)
                message = json.loads(message_raw)
                # Expect: {'cmd': <cmd here>, 'payload': 
                # <arguments here>}

                cmd_func = socket_binds.get(message['cmd'], err)
                print("Dispatch", cmd_func) 
                resp = cmd_func(message, 
                                pool=pool, 
                                callback=
                                websocket_response_callback(
                                    wsock, message.get('cmd', 'err')))

                architecture.log_resp(resp)
                wsock.send(resp)
            except WebSocketError:
                break
            except Exception as e:
                import traceback
                traceback.print_exc()
                wsock.send(json.dumps({'message': 'err', 
                                       'desc': f"{e}"}))
    finally:
        pool.terminate()

def websocket_response_callback(ws, message_type):
    def _callback(payload, err=False):
        if not err:
            resp = json.dumps({
                'message': message_type,
                'payload': payload
            })
        else:
            resp = json.dumps({
                'message': 'err',
                'payload': payload
            })
        print("In callback: ", end='')
        architecture.log_resp(resp)
        ws.send(resp)
    return _callback

def err(message, *args, **kwargs):
    return json.dumps({
        'message': 'err',
        'desc': f"Error: {message['cmd']} not recognised"
    })

def get_subtype(*args, **kwargs):
    return json.dumps({
        'message': 'subtype',
        'subtypes': architecture.get_region_subtypes()
    })

def example_arch(*args, **kwargs):
    return json.dumps({
        'message': 'example_arch',
        'payload': json_to_region.example
    }) 

def run_result(message, *args, 
               pool: AsyncIteratorProcessPool = None, **kwargs):
    print("Running!", str(message)[:min(200, len(str(message)))])
    arch_id = message['payload']['arch_id']
    architecture.run_widget_pool(pool, arch_id)
    return json.dumps({
        'message': 'run_result',
        'payload': 'pending',
    })

def debug_send(message, *args, pool: AsyncIteratorProcessPool = None, **kwargs):
    # Debug:
    architecture.run_debug(pool, next(iter(architecture.saved_architectures.keys())))
    return json.dumps({'message': 'debug'})

def get_router(*args, **kwargs):
    return json.dumps({
        'message': 'get_router',
        'payload': architecture.get_router_mapping()
    })

def get_args(*args, **kwargs):
    return json.dumps({
        'message': 'get_args',
        'payload': architecture.get_region_arguments()
    })

def use_arch(message, *args, **kwargs):
    arch_obj = message['payload']

    return json.dumps({
        'message': 'use_arch',
        'arch_id': architecture.save_arch(arch_obj)
    })

def get_graph(message, *args, **kwargs):
    gobj = message['payload']
    return json.dumps({
            'message': 'get_graph',
            'payload' : {
                'gid' : gobj['gid'], #super silly
                'graph_view' : architecture.retrieve_graph_segment(gobj)
            }
        })

# Socket commands
socket_binds = {
        'subtype': get_subtype,
        'use_arch': use_arch,
        'example_arch': example_arch,
        'run_result': run_result,
        'get_router': get_router,
        'get_args': get_args,
        'get_graph' : get_graph,
        'debug_send': debug_send,
        } 

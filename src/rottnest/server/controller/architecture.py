from bottle import request, abort 
from geventwebsocket import WebSocketError
from rottnest.region_builder import json_to_region
from rottnest.server.model import architecture 

import json

def register_routes(app):
   app.route("/websocket", callback=handle_websocket)

# TODO: Register architecture object
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    while True:
        # TODO: RPC this whole thing
        try:
            message_raw = wsock.receive()
            if message_raw is None: continue
            print(message_raw)
            message = json.loads(message_raw)
            # Expect: {'cmd': <cmd here>, 'payload': <arguments here>}
            cmd_func = socket_binds.get(message['cmd'], err)
            print("Dispatch", cmd_func) 
            resp = cmd_func(message)
            resp_log = str(resp)
            if len(resp_log) > 200:
                resp_log = resp_log[:200] + '<... output truncated>'
            print("Resp:", resp_log)
            wsock.send(resp)
        except WebSocketError:
            break
        except Exception as e:
            import traceback
            traceback.print_exc()
            wsock.send(json.dumps({'message': 'err', 'desc': f"{e}"}))

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

def run_result(message, *args, **kwargs):
    print("Running!", message)
    arch_id = message['payload']['arch_id']
    return json.dumps({
        'message': 'run_result',
        'payload': architecture.run_widget_scheduler(arch_id)
    })

def get_router(*args, **kwargs):
    return json.dumps({
        'message': 'get_router',
        'payload': architecture.get_router_mapping()
    })

def use_arch(message, *args, **kwargs):
    arch_obj = message['payload']

    return json.dumps({
        'message': 'use_arch',
        'arch_id': architecture.save_arch()
    })

# Socket commands
socket_binds = {
        'subtype': get_subtype,
        'use_arch': use_arch,
        'example_arch': example_arch,
        'run_result': run_result,
        'get_router': get_router,
        } 

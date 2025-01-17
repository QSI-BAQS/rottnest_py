from bottle import request, abort 
from geventwebsocket import WebSocketError
from rottnest.region_builder import json_to_region
from rottnest.server.model import architecture 

import json

saved_architectures = {}

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
            print("Resp:", resp)
            wsock.send(resp)
        except WebSocketError:
            break
        except Exception as e:
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
    from ...widget_compilers.main import run as run_widget
    arch_id = message['payload']['arch_id']
    result = run_widget(region_obj=saved_architectures[arch_id])
    return json.dumps({
        'message': 'run_result',
        'payload': result.json
    })


def use_arch(message, *args, **kwargs):
    arch_obj = message['payload']
    import random
    arch_id = random.randint(1000000, 9999999)
    while arch_id in saved_architectures: arch_id = random.randint(1000000, 9999999)

    saved_architectures[arch_id] = arch_obj

    return json.dumps({
        'message': 'use_arch',
        'arch_id': arch_id
    })

# Socket commands
socket_binds = {
        'subtype': get_subtype,
        'use_arch': use_arch,
        'example_arch': example_arch,
        'run_result': run_result
        } 

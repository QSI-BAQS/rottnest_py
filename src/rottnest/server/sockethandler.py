from bottle import request, abort 
from geventwebsocket import WebSocketError
from threading import Semaphore
from rottnest.server.model import architecture 
from rottnest.server.application import RottApplication
from rottnest.server.responder import responder
import json

resp = responder.responder

def register_routes(app):
   app.route("/websocket", callback=handle_websocket)

# TODO: Register architecture object
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    wsock_sem = Semaphore()
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    
    app = RottApplication(wsock, wsock_sem)
    socket_binds = responder.fullqual_map()

    try:
        while True:
            # TODO: RPC this whole thing
            try:
                message_raw = wsock.receive()
                if message_raw is None:
                    continue
                print(message_raw)
                message = json.loads(message_raw)
                # Expect: {'message': <cmd here>, 'payload': 
                # <arguments here>}

                cmd_func = socket_binds.get(message['message'], err)
                print("Dispatch", cmd_func)
                resp = cmd_func(app, message,
                                callback=websocket_response_callback(
                                    wsock, message.get('message', 'err')))

                architecture.log_resp(resp)
                with wsock_sem:
                    wsock.send(resp)
            except WebSocketError:
                break
            except Exception as e:
                import traceback
                traceback.print_exc()
                wsock.send(json.dumps({'message': 'err', 
                                       'desc': f"{e}"}))
    finally:
        pass
        # cu_executor_pool.terminate()

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
        'desc': f"Error: {message['message']} not recognised"
    })



#def debug_send(message, *args, wsock=None, **kwargs):
    # Debug:
    # architecture.run_debug(next(iter(saved_architectures.keys())), wsock)
    # return get_status({'cu_id': 'debug'})
    
#    return architecture.run_debug2(next(iter(saved_architectures.keys())))



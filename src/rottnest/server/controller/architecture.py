from bottle import request, abort 
from geventwebsocket import WebSocketError

from rottnest.server.model import architecture 

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
            message = wsock.receive()
            result = socket_binds.get(message, err) 
            wsock.send(result(message))
        except WebSocketError:
            break

def err(message, *args, **kwargs):
    return f"Error: {message} not recognised"

def get_subtype(*args, **kwargs):
    return json.dumps(architecture.get_subtype())

# Socket commands
socket_binds = {'subtype': get_subtype} 

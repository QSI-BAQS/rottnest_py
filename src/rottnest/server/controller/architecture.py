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
        try:
            message = wsock.receive()
            result = socket_binds.get(message, f"Error: {message} not recognised") 
            wsock.send(result)
        except WebSocketError:
            break

def get_subtype():
    return json.dumps(architecture.get_subtype())

# Socket commands
socket_binds = {'subtype': get_subtype} 

from bottle import request, abort 
from geventwebsocket import WebSocketError



def register_routes(app):
   app.route("/websocket", callback=handle_websocket) 

def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = wsock.receive()
            wsock.send("Your message was: %r" % message)
        except WebSocketError:
            break


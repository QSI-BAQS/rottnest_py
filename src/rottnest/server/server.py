from gevent.pywsgi import WSGIServer
from bottle import Bottle
from geventwebsocket.handler import WebSocketHandler

app = Bottle()

from rottnest.server.controller import architecture

architecture.register_routes(app)

# Global lock
compilation_lock = False


def run(hostname="localhost", port=8080):
    '''
        Runs the server
    '''
    server = WSGIServer(
        (hostname, port),
        app,
        handler_class=WebSocketHandler)
    server.serve_forever()

'''
Rottnest Server - Launches the server and will ready the application
    and debug monitor for the system.

    Make sure the environment.py file is imported to ensure process control
'''
from rottnest import environment
from bottle import Bottle
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from rottnest.server.websocket import sockethandler

app = Bottle()
sockethandler.websocket_register_routes(app)

DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 8080

def rottnestpy_server_start(hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT):
    '''
        Runs the server - Returns a server instance
    '''
    server = WSGIServer(
        (hostname, port),
        app, handler_class=WebSocketHandler)
    return server


def rottnestpy_start():
    '''
       Main method for the server, starts the server
       and allows the  
    '''    
    server_handle = rottnestpy_server_start()
    server_handle.serve_forever()
    
if __name__ == '__main__':
    rottnestpy_start()

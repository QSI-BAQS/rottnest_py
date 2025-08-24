#from rottnest.server.model.architecture import cu_executor_pool

import gevent
from gevent.threadpool import ThreadPool
from gevent.pywsgi import WSGIServer
from bottle import Bottle
from geventwebsocket.handler import WebSocketHandler
from rottnest.debug.monitor import DebugMonitor
from rottnest.server import sockethandler


app = Bottle()
sockethandler.register_routes(app)

# Global lock
compilation_lock = False


def server_start(hostname="localhost", port=8080):
    '''
        Runs the server
    '''
    server = WSGIServer(
        (hostname, port),
        app,
        handler_class=WebSocketHandler)
    #server.start()
    #server.serve_forever()
    return server

if __name__ == '__main__':
    DebugMonitor.with_obj('Server started', 'Server')
    #cu_executor_pool.start()
    #cu_executor_pool.ping()
    
    monitor_obj = DebugMonitor.current()
    pool = ThreadPool(10)
    pool.spawn(monitor_obj.get_console().selector_interact)
    server_handle = server_start()
    server_handle.serve_forever()
    gevent.wait()    

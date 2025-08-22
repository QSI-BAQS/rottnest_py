#from rottnest.server.model.architecture import cu_executor_pool

import gevent
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


def server_wait_closure(server):

    def srv_serve():
        server.serve_forever()

    return srv_serve
    

if __name__ == '__main__':
    DebugMonitor.with_obj('Server started', 'Server')
    #cu_executor_pool.start()
    #cu_executor_pool.ping()
    finished = False

    monitor_obj = DebugMonitor.current()
    jobs = []
    server_handle = server_start()
    srv_obj = gevent.spawn(server_wait_closure(server_handle))
    jobs.append(srv_obj)
    if monitor_obj.stdin_enabled():
        jobs.append(gevent.spawn(monitor_obj.get_console().interact_closure()))
        
    while not finished:
        gevent.wait(jobs, timeout=10)
        print("Do you timeout?")

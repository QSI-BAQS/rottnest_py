
from bottle import Bottle
from gevent.threadpool import ThreadPool
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from rottnest.debug.monitor import DebugMonitor
from rottnest.debug.util import with_debug_log
from rottnest.server import sockethandler
from rottnest.server.app.application import RottnestApplication
from rottnest.server.model.plugin_architecture import cu_executor_pool

app = Bottle()
sockethandler.websocket_register_routes(app)

# Global lock
compilation_lock = False

@with_debug_log(msg="Server Starting")
def server_start(hostname="localhost", port=8080):
    '''
        Runs the server
    '''
    server = WSGIServer(
        (hostname, port),
        app, handler_class=WebSocketHandler)
    return server


@with_debug_log(msg="RottnestPy Init")
def rottnestpy_start():
    monitor_obj = DebugMonitor.default()\
        .get_console()\
        .set_app(RottnestApplication(None, None))\
        .get_monitor()
        
    cu_executor_pool.start()
    cu_executor_pool.ping_manager()
    
    pool = ThreadPool(10)
    pool.spawn(monitor_obj.get_console().selector_interact)
    server_handle = server_start()
    server_handle.serve_forever()
    

if __name__ == '__main__':
    rottnestpy_start()

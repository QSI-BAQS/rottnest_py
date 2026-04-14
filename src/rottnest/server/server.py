from geventwebsocket.websocket import WebSocket

from bottle import Bottle
# from gevent.threadpool import ThreadPool
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from rottnest.debug.monitor import DebugMonitor
from rottnest.debug.util import with_debug_log
from rottnest.server import sockethandler
from rottnest.server.app.application import RottnestApplication

app = Bottle()
sockethandler.websocket_register_routes(app)

# Global lock
compilation_lock = False

thread_pool_count = 4

@with_debug_log(msg="Server Starting")
def server_start(hostname="localhost", port=8080):
    '''
        Runs the server
    '''
    server = WSGIServer(
        (hostname, port),
        app, handler_class=WebSocketHandler)
    return server


# @with_debug_log(msg="RottnestPy Init")
def rottnestpy_start():
    # _monitor_obj = DebugMonitor.default()\
        # .get_console()\
        # .set_app(RottnestApplication.get_uninitialised_instance())\
        # .get_monitor()

    # DEBUG!
    #
    # 

    # webclose = WebSocket.close

    
    def close_wrapper(self, *args, **kwargs):
        print("CLOSING!!!", flush=True)
        self._base_close(*args, **kwargs)
    
    WebSocket._base_close = WebSocket.close
    WebSocket.close = close_wrapper
          
    # pool = ThreadPool(thread_pool_count)
    # pool.spawn(monitor_obj.get_console().selector_interact)
    server_handle = server_start()
    server_handle.serve_forever()
    

if __name__ == '__main__':
    rottnestpy_start()

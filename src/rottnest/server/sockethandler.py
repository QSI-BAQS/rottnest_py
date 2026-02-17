from bottle import request, abort 
from geventwebsocket import WebSocketError
from threading import Semaphore

from rottnest.debug.monitor import DebugMonitor
from rottnest.server.app.application import RottnestApplication

# TODO: This is marked for removal
# These are used register routes which are core
# from rottnest.server.responder import responder
# from rottnest.server.controller import prgs
# from rottnest.server.controller.arch import meta, callgraph
# from rottnest.server.controller import data


from rottnest.server.controller.architecture import ArchitectureInterface
from rottnest.server.controller.executable import ExecutableInterface
from rottnest.server.controller_mapper import ControllerMapper
from rottnest.debug.util import with_debug_log

import json


@with_debug_log()
def websocket_register_routes(app):
    
    DebugMonitor.with_obj('Registering routes', __name__)
    app.route("/websocket", callback=websocket_handle)

@with_debug_log()
def websocket_construct():
    wsock = request.environ.get('wsgi.websocket')
    wsock_sem = Semaphore()

    if not wsock:
        abort(400, 'Expected WebScoket request.')

    return (wsock, wsock_sem)

@with_debug_log()
def websocket_handle():
    
    wsock, wsock_sem = websocket_construct()
    
    app = RottnestApplication(wsock, wsock_sem)
    DebugMonitor  \
        .current()\
        .set_console_context(app)

    
    socket_binds = ControllerMapper.assemble() \
        .attach(ArchitectureInterface) \
        .attach(ExecutableInterface) \
        .build()
    

    try:
        while True:

            DebugMonitor.with_obj('Listening and waiting for messages', __name__)
            try:
                message_raw = wsock.receive()
                if message_raw is None:
                    continue
                DebugMonitor.with_obj(message_raw, __name__)
                message = json.loads(message_raw)
                # Expect: {'message': <cmd here>, 'payload': 
                # <arguments here>}

                # cmd_func = socket_binds.get(message['message'], err)
                cmd_func = socket_binds.get(message['message'], err)
                DebugMonitor.with_obj(cmd_func, 'SocketHandler::cmd_func')
                print("Dispatch", cmd_func)
                DebugMonitor.with_obj(message, 'Dispatch')

                resp = cmd_func(app, message,
                                callback=websocket_response_callback(
                                    wsock, message.get('message', 'err')))

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

@with_debug_log()
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
        ws.send(resp)
    return _callback

@with_debug_log()
def err(app, message, *args, **kwargs):
    print(str(message))
    return json.dumps({
        'message': 'err',
        'desc': f"Error: {message['message']} not recognised"
    })


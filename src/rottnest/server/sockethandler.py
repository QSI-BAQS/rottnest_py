from bottle import request, abort 
from geventwebsocket import WebSocketError
from threading import Semaphore

from rottnest.debug.monitor import DebugMonitor
from rottnest.server.app.application import RottnestApplication

from rottnest.server.controller.architecture import ArchitectureInterface
from rottnest.server.controller.executable import ExecutableInterface
from rottnest.server.controller.callgraph import CallGraphInterface
from rottnest.server.controller.layout import LayoutInterface
from rottnest.server.controller.data import RunResultDataInterface
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

    socket_binds = ControllerMapper.assemble(app.get_responder_ref()) \
        .attach(ArchitectureInterface) \
        .attach(ExecutableInterface) \
        .attach(LayoutInterface) \
        .attach(CallGraphInterface) \
        .attach(RunResultDataInterface) \
        .build()

    try:
        while True:
            try:
                message_raw = wsock.receive()
                success, message = websocket_message_deserialize(message_raw)

                if success:
                    websocket_dispatch_handle(wsock, wsock_sem, \
                                              app, message, \
                                              socket_binds)

            except WebSocketError as wse:
                DebugMonitor.dump(str(wse))
                break
            except Exception as e:
                import traceback
                traceback.print_exc()
                DebugMonitor.dump(traceback.format_exc())
                wsock.send(json.dumps({'message': 'err', 
                                       'desc': f"{e}"}))
    finally:
        pass
        # cu_executor_pool.terminate()

@with_debug_log()
def websocket_message_deserialize(message_raw) -> tuple[bool, dict]:
    '''
        Wraps the deserialisation of the messages received 
    '''
    message = dict()
    
    if message_raw is None: # Early return if the message is empty
        return (False, {})

    try:
        message = json.loads(message_raw)
    except json.JSONDecodeError as jde:
        DebugMonitor.dump(jde.msg)
        return (False, {})
    return (True, message)


@with_debug_log()
def websocket_dispatch_handle(wsock, wsock_sem, app, message, cntrlmapper):
    '''
       Handling of the websocket when a message is received 
    '''
    cmd_func = cntrlmapper.get(message['message'], err)
    resp = cmd_func(app, message,
                    callback=websocket_response_callback(
                        wsock, message.get('message', 'err')))
    with wsock_sem:
        wsock.send(resp)


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
        # print("In callback: ", end='')
        ws.send(resp)
    return _callback

@with_debug_log()
def err(app, message, *args, **kwargs):
    # print(str(message))
    return json.dumps({
        'message': 'err',
        'desc': f"Error: {message['message']} not recognised"
    })


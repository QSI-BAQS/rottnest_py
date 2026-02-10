from bottle import request, abort 
from geventwebsocket import WebSocketError
from threading import Semaphore

from rottnest.debug.monitor import DebugMonitor
from rottnest.server.app.application import RottnestApplication
from rottnest.server.responder import responder

# These are used register routes which are core
# TODO: We need to revise this component
from rottnest.server.controller import prgs
from rottnest.server.controller.arch import meta, callgraph
from rottnest.server.controller import data


from rottnest.server.controller.architecture import ArchitectureInterface
from rottnest.server.controller.executable import ExecutableInterface
from rottnest.server.controller_mapper import ControllerMapper


import json

resp = responder

def register_routes(app):
    
    DebugMonitor.with_obj('Registering routes', __name__)
    app.route("/websocket", callback=handle_websocket)

# TODO: Register architecture object
def handle_websocket():

    DebugMonitor.with_obj('handle_websocket started', __name__)
    wsock = request.environ.get('wsgi.websocket')
    wsock_sem = Semaphore()
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    
    app = RottnestApplication(wsock, wsock_sem)
    DebugMonitor.current().get_console().set_app(app)
    DebugMonitor.with_obj('Assigning a new app context', __name__)

    
    #socket_binds = responder.fullqual_map()
    socket_binds = ControllerMapper.assemble() \
        .attach(ArchitectureInterface) \
        .attach(ExecutableInterface) \
        .build()
    
    print('==============')
    print(ArchitectureInterface)

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

def err(app, message, *args, **kwargs):
    print(str(message))
    return json.dumps({
        'message': 'err',
        'desc': f"Error: {message['message']} not recognised"
    })


from bottle import request, abort 
from geventwebsocket import WebSocketError
from threading import Semaphore
from rottnest.server.app.application import RottnestApplication
from rottnest.server.websocket.websocket_pool import WebSocketPoolSelector
from rottnest.server.controller.architecture import ArchitectureInterface
from rottnest.server.controller.executable import ExecutableInterface
from rottnest.server.controller.callgraph import CallGraphInterface
from rottnest.server.controller.layout import LayoutInterface
from rottnest.server.controller.procedure import ProcedureInterface
from rottnest.server.controller.sync import SynchroniseInterface
from rottnest.server.controller.mapper import ControllerMapper
from rottnest.server.websocket.websocket_service import WebSocketService
import json

WSGI_ENV_KEY = 'wsgi.websocket'
WSGI_WS_ROUTE = '/websocket'

WEBSOCKET_MESSAGE_KEY = 'message'
WEBSOCKET_PAYLOAD_KEY = 'payload'
WEBSOCKET_DESCRIPTION_KEY = 'desc'
WEBSOCKET_ERROR_VAL = 'err'
WEBSOCKET_ABORT_MSG = 'Expected WebSocket request.'
WEBSOCKET_ABORT_STATUS = 400

WEBSOCKET_PRINT_TRACEBACK = True

def websocket_reset_rottnest(proxy_instance):
    '''
       Attempts to get a new instance of the app if it is not initialised 
    '''
    app = RottnestApplication.try_get_instance()
    if app is None:
        app = RottnestApplication.get_uninitialised_instance()
    app.set_websocket_proxy(proxy_instance)

    return app
    
def websocket_register_routes(app):
    '''
      Websocket registration of the route  
    '''
    app.route(WSGI_WS_ROUTE, callback=websocket_handle)

def websocket_construct():
    '''
       Websocket construction function that will build
       a websocket and semaphore 
    '''
    wsock = request.environ.get(WSGI_ENV_KEY)
    wsock_sem = Semaphore()

    wsock_service = WebSocketService(wsock)
    
    if not wsock:
        abort(WEBSOCKET_ABORT_STATUS, WEBSOCKET_ABORT_MSG)

    return (wsock_service, wsock_sem)

def websocket_handle():
    '''
       Websocket handler that will be used to process requests from the frontend
       This is a single threaded application
    '''
    wsock, wsock_sem = websocket_construct()
    proxy_instance = WebSocketPoolSelector.get_current_websocket().and_with(
                                                                    wsock,
                                                                    wsock_sem)
    app = websocket_reset_rottnest(proxy_instance)
    
    socket_binds = ControllerMapper.assemble(app.get_responder_ref()) \
        .attach(ArchitectureInterface) \
        .attach(ExecutableInterface) \
        .attach(LayoutInterface) \
        .attach(CallGraphInterface) \
        .attach(ProcedureInterface) \
        .attach(SynchroniseInterface) \
        .build()


    try:
        while True:
            try:
                message_raw = websocket_receive_message(wsock)
                success, message = websocket_message_deserialize(message_raw)

                websocket_dispatch_handle(success,
                                          wsock,
                                          wsock_sem,
                                          app,
                                          message,
                                          socket_binds)

            except WebSocketError as _wse:
                websocket_print_traceback()
                break
            except Exception as e:
                websocket_send_message(wsock, websocket_error_description(e))
    except Exception as _e:
        websocket_print_traceback()

def websocket_print_traceback():
    '''
       Simplifies the traceback printing to this function itself
       Easy switch to re-enable 
    '''
    if WEBSOCKET_PRINT_TRACEBACK:
        import traceback
        traceback.print_exc()

def websocket_receive_message(websocket):
    '''
       Wrapper on the websocket object to handl receiving data 
    '''
    return websocket.receive()

def websocket_send_message(websocket, message: str):
    '''
       Clear wrapper on the object that is sending data 
    '''
    websocket.send(message)

def websocket_error_description(exception_obj):
    '''
       Error message when the backend triggers an exception
    '''
    return json.dumps({
              WEBSOCKET_MESSAGE_KEY: WEBSOCKET_ERROR_VAL, 
               WEBSOCKET_DESCRIPTION_KEY: f"{exception_obj}"})
    
def websocket_message_deserialize(message_raw) -> tuple[bool, dict]:
    '''
        Wraps the deserialisation of the messages received 
    '''
    message = dict()
    if message_raw is None: # Early return if the message is empty
        return (False, {})
    try:
        message = json.loads(message_raw)
    except json.JSONDecodeError as _jde:
        # DebugMonitor.dump(jde.msg)
        return (False, {})
    return (True, message)


def websocket_dispatch_handle(success, wsock, wsock_sem, app, message, cntrlmapper):
    '''
       Handling of the websocket when a message is received 
    '''
    if success:
        cmd_func = cntrlmapper.get(message[WEBSOCKET_MESSAGE_KEY], err)
        resp = cmd_func(app, message,
                        callback=websocket_response_callback(
                            wsock, message.get(WEBSOCKET_MESSAGE_KEY,
                                               WEBSOCKET_ERROR_VAL)))
        with wsock_sem:
            wsock.send(resp)


def websocket_response_callback(ws, message_type):
    '''
       Searches to see if it can find an appropriate method 
    '''
    def _callback(payload, err=False):
        if not err:
            resp = json.dumps({
                WEBSOCKET_MESSAGE_KEY: message_type,
                WEBSOCKET_PAYLOAD_KEY: payload
            })
        else:
            resp = json.dumps({
                WEBSOCKET_MESSAGE_KEY: WEBSOCKET_ERROR_VAL,
                WEBSOCKET_PAYLOAD_KEY: payload
            })
        ws.send(resp)
    return _callback



def err(app, message, *args, **kwargs):
    '''
       Default error that can occur and also get sent tot he frontend
       for it to be displayed for debugging purposes
    '''
    return json.dumps({
        WEBSOCKET_MESSAGE_KEY
            : WEBSOCKET_ERROR_VAL,
        WEBSOCKET_DESCRIPTION_KEY
            : f"Error: {message[WEBSOCKET_MESSAGE_KEY]} not recognised"
    })


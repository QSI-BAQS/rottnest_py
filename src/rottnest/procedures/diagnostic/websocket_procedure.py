from rottnest.procedures.stage import RottnestCompilerStage
from rottnest.procedures.pool import procedure_pool
from rottnest.server.app.application import RottnestApplication

from time import time

import json

STAGE_TAG = 'websocket_diagnostic'

class WebsocketProcedureDiagnostic(RottnestCompilerStage):
    '''
       Gets the websocket and is able to send the diagnostic
       messages to a client that is currently hooked up to it 
    '''

    
    def __init__(self):
        '''
           Gets access to an instance of rottnest application 
        '''
        # NOTE: Should not be an uninitialised version
        self.rottnest_app = RottnestApplication.get_instance()


    def make_diagnostic_message(self):
        '''
           Packages a diagnostic message to be sent
           to a hooked up client 
        '''

        packet = {
            'message': 'rottnest.diagnostic.websocket',
            'payload': time()
        }
        return json.dumps(packet)


    def execute(self, compiler_environment):
        '''
           Is able to get access to the websocket
           and send it back to the frontend 
        '''

        wsock = self.rottnest_app.get_websocket()

        if wsock is not None:
            wsock.send(self.make_diagnostic_message())


    def complete(self):
        '''
           Checks to see if it is complete 
        '''
        return True

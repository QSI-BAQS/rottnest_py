'''
    This interface handles the layout controllers 
'''
from rottnest.procedures.procedure_manager import ProcedureManager
from rottnest.plugins import architectures
from rottnest.plugins import executables
from rottnest.procedures.preprocess_and_execute\
    .procedure_preprocess_and_execute import PreprocAndExecuteProcedure
from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.server.protocol.net import Rottnest
from rottnest.server.app.application import RottnestApplication

from rottnest.debug.util import with_debug_log

import time

STANDARD_DELAY_ON_POLL = 3

RUN_LAYOUT_MSG_END = {
    "message": Rottnest.layout.poll_status,
    "payload": "issued"
}

RUN_LAYOUT_PROCESS_MSG = {
    "message": Rottnest.layout.poll_status,
    "payload": "processing"
}

RUN_LAYOUT_EXEC_ERROR = {
    "message": Rottnest.layout.err.executable_invalid,
}

RUN_LAYOUT_ARCH_ERROR = {
    "message": Rottnest.layout.err.architecture_invalid,
}

STATE_OBJ_APP_KEY = 'application'
STATE_OBJ_PREPROC_KEY = 'preprocessor'

def get_layouts():
        '''
            Gets the list of currently loaded layouts
        '''
        # TODO: You will need to maintain a history of layouts that have
        #       been set

        layouts_available = LayoutProxy.get_layouts()
        return layouts_available

def set_layout(data):
        '''
            Sets a layout that can then be used
        '''
        # TODO: You will need to get this set correctly
        #       - Not sure what data is meant to be represented
        #       - Just guessing on this front
        layout_obj = data
        layout_id = LayoutProxy.add_layout(layout_obj)
        return layout_id
        
@with_debug_log()
def _run_layout_poll(state):
    '''
       Callback function for the run layout call 
    '''
    app = state[STATE_OBJ_APP_KEY]
    preproc = state[STATE_OBJ_PREPROC_KEY]

    if preproc is not None:
        preproc.poll()
    
    #if app is not None:
        #app.websocket_heartbeat()
        # time.sleep(STANDARD_DELAY_ON_POLL)

@with_debug_log()
def _run_layout_finalise(state_obj):
    '''
       Once finished, it will outline that it is complete 
    '''
    pass

def run_layout(layout):
        '''
            Gets the list of currently loaded layouts
        '''
        app = RottnestApplication.get_instance()
        current_exec = executables.get_current_executable()
        current_arch = architectures.get_current_architecture()

        if current_exec is None:
            #
            # Current executable is not set, will be rejected
            # 
            return RUN_LAYOUT_EXEC_ERROR
        elif current_arch is None:
            #
            # Current architecture is not set, will be rejceted
            # 
            return RUN_LAYOUT_ARCH_ERROR
        else:
            #
            # Is able to process the layout, executable and architecture
            # TODO: Change the id to the generated one..
            layout_id = 0
            LayoutProxy.add_layout_with_id(layout_id, layout)

            procedure_manager = ProcedureManager.get_instance()
            preprocessor_stage = PreprocAndExecuteProcedure()
            state_object = {
                STATE_OBJ_APP_KEY: app,
                STATE_OBJ_PREPROC_KEY: preprocessor_stage
            }

            # NOTE: Manager is really just a wrapper in this case
            _result = procedure_manager\
                .execute_defer(preprocessor_stage, _run_layout_poll, _run_layout_finalise, state_object)
            
            return RUN_LAYOUT_MSG_END


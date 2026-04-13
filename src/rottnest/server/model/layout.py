'''
    This interface handles the layout controllers 
'''
from rottnest.procedures.procedure_manager import ProcedureManager
from rottnest.plugins import architectures
from rottnest.plugins import executables
from rottnest.procedures.preprocess_and_execute\
    .procedure_preprocess_and_execute import PreprocAndExecuteProcedure
from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.server.app.application import RottnestApplication
from rottnest.protocol.net import Rottnest

import time
import json

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
        
        

def run_layout(layout):
        '''
            Gets the list of currently loaded layouts
        '''
        # TODO: Please amend this when we have a layout manager in the backend
        #       Please, thank you and bless
        wsock = RottnestApplication.get_instance().get_websocket()
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


            # NOTE: Manager is really just a wrapper in this case
            _result = procedure_manager\
                .execute_immediate(preprocessor_stage, )

            # time.sleep(4) # BUG: If `poll` is called before a process is ready
            # Bad solution: You can sleep by 2 seconds and lets the workers push through
            # 
            # It will result in a crash/reset of the websocket and other components
            # Observed:
            #   - PoolManager/ProcessPool is detached/unmanaged
            #   - New PoolManager/ProcessPool is constructed?
            #   -   This will repeat and there is no way for the pool manager to accept work

            # NOTE: Get an idea from the process pool and its structure
            
            # NOTE/TODO: Probably need to clean this up or restructure it?
            
            while not preprocessor_stage.complete():
                preprocessor_stage.poll()
                # NOTE: Keeping it commented it out   
                # wsock.send(json.dumps(RUN_LAYOUT_PROCESS_MSG))


            # TODO: Send back confirmation that it has started running
            #       This should indicate the kind of state it is in.

            return RUN_LAYOUT_MSG_END


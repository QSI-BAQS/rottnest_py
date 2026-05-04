'''
    This interface handles the layout controllers 
'''
from rottnest.procedures.procedure_manager import ProcedureManagerSelector, MPSCChannelProvider, \
    MPSC_LAYOUT_CHANNEL_TAG
from rottnest.plugins import architectures
from rottnest.plugins import executables
from rottnest.procedures.preprocess_and_execute\
    .procedure_preprocess_and_execute import PreprocAndExecuteProcedure
from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.server.protocol.net import Rottnest
from rottnest.server.app.application import RottnestApplication
from rottnest.server.websocket.websocket_pool import WebSocketPoolSelector

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
        

def run_layout(layout):
        '''
            Gets the list of currently loaded layouts
        '''
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
            layout_obj = layout
            _layout_id = LayoutProxy.add_layout_with_id(0, layout_obj)
            app = RottnestApplication.get_instance()
            mpsc_provider: MPSCChannelProvider = MPSCChannelProvider.get_instance()
            mpsc_provider.recreate_channel(MPSC_LAYOUT_CHANNEL_TAG)
            mpsc_reader, _mpscstate = mpsc_provider.get_reader(MPSC_LAYOUT_CHANNEL_TAG)
                
            procedure_manager = ProcedureManagerSelector.get_instance().get_default(app)
            preprocessor_stage = PreprocAndExecuteProcedure()
            websocket = WebSocketPoolSelector.get_current_websocket().get_proxy()
            websocket.Layout.run_layout(websocket,
                                        preprocessor_stage,
                                        procedure_manager,
                                        mpsc_reader)
            
            return RUN_LAYOUT_MSG_END


'''
    This interface handles the layout controllers 
'''
from rottnest.plugins import architectures
from rottnest.plugins import executables
# from rottnest.server.util.result import Result
from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.procedures import preprocessor


RUN_LAYOUT_MSG_TEMP = {
    "layout_id": 0,
    "status": "started"
}


def get_layouts():
        '''
            Gets the list of currently loaded layouts
        '''
        pass

def set_layout(data):
        '''
            Sets a layout that can then be used
        '''
        pass

def run_layout(layout):
        '''
            Gets the list of currently loaded layouts
        '''
        # TODO: Please amend this when we have a layout manager in the backend
        #       Please, thank you and bless

        print(executables.get_current_executable())
        print(architectures.get_current_architecture())

        # TODO: Change the id to the generated one..
        layout_id = 0
        LayoutProxy.add_layout_with_id(layout_id, layout)
        
        proc = preprocessor.PreprocessorProcedure()
        proc.execute()

        while not proc.complete():
            proc.poll()

        print("Running a quick test")

        # TODO: Send back confirmation that it has started running
        #       This should indicate the kind of state it is in.

        return RUN_LAYOUT_MSG_TEMP

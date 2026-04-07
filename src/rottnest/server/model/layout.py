'''
    This interface handles the layout controllers 
'''
from rottnest.plugins import architectures
from rottnest.plugins import executables
from rottnest.procedures import preprocessor
from rottnest.compute_units.layout_proxy import LayoutProxy

RUN_LAYOUT_MSG_TEMP = {
    "layout_id": 0,
    "status": "started"
}

RUN_LAYOUT_EXEC_ERROR = {
    'message': 'layout_executable_invalid'
}

RUN_LAYOUT_ARCH_ERROR = {
    'message': 'layout_architecture_invalid'
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
    
            proc = preprocessor.PreprocessorProcedure()
            proc.execute()

            while not proc.complete():
                proc.poll()

            print("Running a quick test")

            # TODO: Send back confirmation that it has started running
            #       This should indicate the kind of state it is in.

            return RUN_LAYOUT_MSG_TEMP


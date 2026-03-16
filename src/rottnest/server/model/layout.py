'''
    This interface handles the layout controllers 
'''
from rottnest.plugins import architectures as singleton
from rottnest.server.util.result import Result


def get_layouts(message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded layouts
        '''
        pass

def set_layout(message, **kwargs) -> Result:
        '''
            Sets a layout that can then be used
        '''
        pass

def run_layout(message, **kwargs) -> Result:
        '''
            Gets the list of currently loaded layouts
        '''
        pass

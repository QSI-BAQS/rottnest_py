'''
    Designer proxy for the preprocessor
    Mostly just sets a memory bound on the widgetisation
    While satisfying the architecture interface
'''
from rottnest.architecture_interface import rottnest_designer


class PreprocessDesigner(rottnest_designer.RottnestDesigner):
    '''
        Designer proxy for the preprocessor
        Mostly just sets a memory bound on the widgetisation
        While satisfying the architecture interface
    '''

    DEFAULT_MEM_BOUND = 1000

    @classmethod
    def get_mem_bound(cls, *_args, **_kwargs):
        '''
            Const getter
        '''
        return cls.DEFAULT_MEM_BOUND

    @staticmethod
    def get_designer_metadata():
        '''
           Gets the designer metadata for the frontend that will
           outline the position of the frontend files to be loaded
        '''
        return []

    @staticmethod
    def get_designer_data():
        '''
           Gets the designer data for the backend that will
           outline functions that will be callable by when
           messages map to the websocket protocol
        '''
        return {
            "api": {
                "mask": "rz_counter",
                "spec": []
            }
        }

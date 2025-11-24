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
    def get_mem_bound(cls, *args, **kwargs):
        return cls.DEFAULT_MEM_BOUND

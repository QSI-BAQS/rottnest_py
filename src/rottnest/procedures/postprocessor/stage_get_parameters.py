'''
    Stage for synchronising the option module with the pool manager 
'''
from rottnest.procedures import stage

STAGE_TAG =  'get_postprocessor_parameters'

class GetPostprocessorParametersStage(stage.RottnestCompilerStage):
    '''
        Sets parameters for the postprocessor        
    '''

    TAG = STAGE_TAG

    def __init__(
            self,
            *,
            tag=None,
            dependencies=None
        ):

        self.result = None
 
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=True
        )

    def __call__(self):
        '''
            Overload the caller
        '''
        return self.result

    def execute(self, compiler_environment):
        '''
            Submit to the procedure manager to get parameters 
        '''
        from rottnest.process_pool import get_pool
        pool = get_pool()
        pool.get_postprocessor_parameters()

    def poll(self, compiler_environment):
        '''
            Polling method
        '''
        from rottnest.process_pool import get_pool
        pool = get_pool()
        obj = pool.poll_postprocessor_parameters()
        if obj is not None:
            self.result = obj
            self._complete = True


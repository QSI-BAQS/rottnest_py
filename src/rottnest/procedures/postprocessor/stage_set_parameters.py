'''
    Stage for synchronising the option module with the pool manager 
'''
from rottnest.procedures import stage

STAGE_TAG =  'get_postprocessor_parameters'

class SetPostprocessorParametersStage(stage.RottnestCompilerStage):
    '''
        Sets parameters for the postprocessor        
    '''

    TAG = STAGE_TAG

    def __init__(
            self,
            parameters,
            *,
            tag=None,
            dependencies=None
        ):

        self.parameters = parameters       
 
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Synchronises with the process pool  
        '''

        from rottnest.process_pool import get_pool
        pool = get_pool()
        pool.set_postprocessor_parameters(self.parameters)
        self._complete = True

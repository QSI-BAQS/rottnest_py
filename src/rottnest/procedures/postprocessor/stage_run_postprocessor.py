'''
    Stage for synchronising the option module with the pool manager 
'''
from rottnest.procedures import stage

STAGE_TAG =  'get_postprocessor_result'

class RunPostprocessorStage(stage.RottnestCompilerStage):
    '''
        Gets postprocessor output 
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
            asynchronous=False
        )

    def get_result(self):
        '''
            Getter for the result
        '''
        return self.result

    def __call__(self):
        '''
            Dispatch to get_result
        '''
        return self.get_result()

    def execute(self, compiler_environment):
        '''
            Synchronises with the process pool  
        '''

        from rottnest.process_pool import get_pool
        pool = get_pool()
        pool.run_postprocessor()

    def poll(self):
        '''
            Poll handler
        '''
        from rottnest.process_pool import get_pool
        pool = get_pool()
        res = pool.poll_postprocessor() 
        if res is not None:
            self.result = res
            self._complete = True
        

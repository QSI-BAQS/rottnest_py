'''
    Simple setter for the error budget
    TODO: Extend this with the plugin system for different budget setters
'''
from rottnest.procedures import stage
from rottnest.process_pool import terminate_pool

STAGE_TAG = 'terminate_pool'

class TerminatePoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, target_error=None, p_phys=None):
        '''
            Constructor
        '''

        self._complete = False
        if dependencies is None:
            dependencies = [] 
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Synchronises and starts the workers
        '''

        terminate_pool()

        self._complete = True

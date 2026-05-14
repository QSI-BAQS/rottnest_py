from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool

from . import stage_start_pool_manager

STAGE_TAG = 'Reset Pool Context'

class ResetContextStage(stage.RottnestCompilerStage):
    '''
        Resets the execution context
    '''
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_start_pool_manager.STAGE_TAG] 
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Synchronises and starts the workers
        '''
        pool = get_pool()
        pool.reset_execution_context()

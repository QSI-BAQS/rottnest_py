from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool import commands

from . import stage_start_pool_manager

STAGE_TAG = 'Clear Pool Buffers'

class ClearPoolBuffersStage(stage.RottnestCompilerStage):
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
        pool.clear_buffers(
            commands.GET_CURRENT_RESULTS,
            commands.GET_RESULTS_STREAM,
        )

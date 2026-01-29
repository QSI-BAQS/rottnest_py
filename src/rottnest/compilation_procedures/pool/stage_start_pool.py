from rottnest.compilation_procedures import stage
from rottnest.process_pool.singleton import get_pool

from . import stage_start_pool_manager

STAGE_TAG = 'Start Pool'

class StartPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_start_pool_manager.STAGE_TAG] 
        super().__init__(tag=tag, dependencies=dependencies)

    def execute(self, environment):
        '''
            Synchronises and starts the workers
        '''
        pool = get_pool()
        pool.synchronise()
        pool.start_workers()

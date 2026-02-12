from rottnest.compilation_procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus

from . import stage_synchronise

STAGE_TAG = 'Start Pool'

class StartPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_synchronise.STAGE_TAG] 
        self._complete = False
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, environment):
        '''
            Synchronises and starts the workers
        '''
        pool = get_pool()
        pool.start_workers()

    def poll(self, environment):
        pool = get_pool()
        self._complete = (pool.poll() == PoolStatus.STARTED_WORKERS)


    def complete(self):
        return self._complete

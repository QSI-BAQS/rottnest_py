from rottnest.compilation_procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus

from . import stage_start_pool_manager

STAGE_TAG = 'Synch Pool'

class SynchronisePoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_start_pool_manager.STAGE_TAG] 
        self._complete = False
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=True
        )

    def execute(self, environment):
        '''
            Synchronises and starts the workers
        '''
        pool = get_pool()
        pool.synchronise()

    def poll(self, environment):
        pool = get_pool()
        status = pool.get_status()
        self._complete = (pool.get_status() == PoolStatus.SYNCHRONISED)

    def complete(self):
        return self._complete

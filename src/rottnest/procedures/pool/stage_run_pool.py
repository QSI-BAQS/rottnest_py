from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus

from . import stage_start_pool

STAGE_TAG = 'Run Pool'

class RunPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_start_pool.STAGE_TAG] 

        self._complete = False

        super().__init__(tag=tag, dependencies=dependencies, asynchronous=True)



    def execute(self, compiler_environment):
        # TODO: load layout IDs
        pool = get_pool()
        pool.run_sequence([0])

    def poll(self, compiler_environment):
        '''
            Checks if the pool has finished
        '''
        pool = get_pool()
        self._complete = (
            pool.poll() == PoolStatus.FINISHED
        )

    def complete(self):
        return self._complete

from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool

from . import stage_run_pool

STAGE_TAG = 'Shutdown Pool'

class ShutdownPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, asynchronous=True):
        if dependencies is None:
            dependencies = [stage_run_pool.STAGE_TAG] 

        self._complete = False

        super().__init__(tag=tag, dependencies=dependencies, asynchronous=asynchronous)

    def execute(self, compiler_environment):
        pool = get_pool()
        pool.shutdown()

    def poll(self, compiler_environment):
        pool = get_pool()
        self._complete = pool.shutdown_status()
        
    def complete(self):
        return self._complete

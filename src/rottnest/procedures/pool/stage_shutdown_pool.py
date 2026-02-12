from rottnest.compilation_procedures import stage
from rottnest.process_pool.singleton import get_pool

from . import stage_run_pool

STAGE_TAG = 'Shutdown Pool'

class ShutdownPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_run_pool.STAGE_TAG] 
        super().__init__(tag=tag, dependencies=dependencies)

    def execute(self, environment):
        pool = get_pool()
        pool.shutdown()

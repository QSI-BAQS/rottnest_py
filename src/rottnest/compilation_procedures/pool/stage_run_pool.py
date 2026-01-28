from rottnest.compilation_procedures import stage
from rottnest.process_pool.singleton import get_pool

from . import stage_start_pool

STAGE_TAG = 'Run Pool'

class RunPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_start_pool.STAGE_TAG] 
        super().__init__(tag=tag, dependencies=dependencies)

    def execute(self, environment):
        # TODO: load layout IDs
        pool = get_pool()
        pool.run_sequence([0])

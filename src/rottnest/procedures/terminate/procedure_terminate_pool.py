from rottnest.procedures import procedure
from .stage_terminate_pool import TerminatePoolStage

STAGE_TAG = 'terminate_pool'

class TerminatePoolProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, target_error=None, p_phys=None):

        stage = TerminatePoolStage(
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

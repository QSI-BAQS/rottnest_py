from rottnest.procedures import procedure

from . import stage_set_architecture

STAGE_TAG = 'set_architecture_procedure'

class SetArchitectureProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, architecture, *, tag=None, dependencies=None):

        stage = stage_set_architecture.SetArchitectureStage(
                architecture = architecture,
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

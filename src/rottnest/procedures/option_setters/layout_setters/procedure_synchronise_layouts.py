from rottnest.procedures import procedure

from .stage_synchronise_layouts import SynchroniseLayoutsStage


STAGE_TAG = 'synchronise_layouts_procedure'

class SynchroniseLayoutsProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, layouts, *, tag=None, dependencies=None):

        # TODO: Replace this with dynamic loads

        stage = SynchroniseLayoutsStage(
                layouts = layouts,
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

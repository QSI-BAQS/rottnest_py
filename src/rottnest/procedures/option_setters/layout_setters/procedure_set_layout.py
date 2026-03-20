from rottnest.procedures import pool, procedure

from . import stage_set_layout


STAGE_TAG = 'set_layout_procedure'

class SetLayoutProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, layout, *, tag=None, dependencies=None):

        # TODO: Replace this with dynamic loads

        stage = stage_set_layout.SetLayoutStage(
                layout = layout,
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

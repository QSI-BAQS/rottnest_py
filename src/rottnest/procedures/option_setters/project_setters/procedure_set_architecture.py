from rottnest.procedures import procedure

from . import stage_set_architecture
from . import stage_synchronise_architecture


STAGE_TAG = 'set_architecture_procedure'

class SetArchitectureProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, architecture, *, pool=True, tag=None, dependencies=None):

        stage_set = stage_set_architecture.SetArchitectureStage(
                architecture = architecture,
                dependencies = []
        )
        stages = [stage_set]

        if pool:
            stage_synch = stage_synchronise_architecture.SynchroniseArchitectureStage(
                    dependencies = [stage_set.get_tag()]
            )
            stages.append(stage_synch)

        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

from rottnest.procedures import procedure

from .stage_load_architectures import LoadArchitecturesStage
from .stage_load_executables import LoadExecutablesStage

STAGE_TAG = 'load_modules_procedure'

class LoadModulesProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(
         self,
         architectures: list,
         executables: list,
         *,
         tag=None,
         dependencies=None):
        
        stage_arch = LoadArchitecturesStage(
                architectures=architectures,
                dependencies = []
        )
        stage_exec = LoadExecutablesStage(
                executables=executables,
                dependencies = []
        )
        stages = [
            stage_arch,
            stage_exec
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

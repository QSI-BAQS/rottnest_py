from rottnest.procedures import procedure

from . import stage_set_executable

STAGE_TAG = 'set_executable_procedure'

class SetExecutableProcedure(procedure.RottnestCompilerProcedure): 
    '''
        Wrapper for the set executable procedure
        Currently mostly boilerplate, but helps protect against wild state updates 
    '''

    TAG = STAGE_TAG

    def __init__(self, executable, *, tag=None, dependencies=None):

        stage = stage_set_executable.SetExecutableStage(
                executable = executable,
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

from rottnest.procedures import procedure

from . import stage_set_executable
from . import stage_synchronise_executable


STAGE_TAG = 'set_executable_procedure'

class SetExecutableProcedure(procedure.RottnestCompilerProcedure): 
    '''
        Wrapper for the set executable procedure
        Currently mostly boilerplate, but helps protect against wild state updates 
    '''

    TAG = STAGE_TAG

    def __init__(self, executable, params, *, pool=True, tag=None, dependencies=None):

        stage_set = stage_set_executable.SetExecutableStage(
                executable = executable,
                params = params,
                dependencies = []
        )
        stages = [stage_set]
    
        if pool:

            stage_synch = stage_synchronise_executable.SynchroniseExecutableStage(
                    dependencies = [stage_set.get_tag()]
            )
            stages.append(stage_synch) 

        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

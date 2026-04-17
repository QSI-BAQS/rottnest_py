'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.plugins import executables

STAGE_TAG = 'set_executable'

class SetExecutableStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(
            self,
            executable: str,
            *,
            params=None,
            tag=None,
            dependencies=None
        ):
        self._complete = False
        self._executable = executable
        self._params = params
        
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Swaps the current rottnest executable 
        '''
        executables.set_current_executable(self._executable)

        if self._params is not None:
            executables.set_executable_params(**self._params)

        self._complete = True


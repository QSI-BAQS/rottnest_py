'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.plugins import executables

STAGE_TAG = 'set_executable_params'

class SetExecutableParamsStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, executable: str, *, tag=None, dependencies=None):
        self._complete = False
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
        executables.set_executable_params(self._params)
        self._complete = True

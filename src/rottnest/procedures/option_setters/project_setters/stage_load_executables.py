'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.plugins import executables

STAGE_TAG = 'load_executables'

class LoadExecutablesStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, executables: list, *, tag=None, dependencies=None):
        self._complete = False
        self._executables = executables
        
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Swaps the current rottnest architecture 
        '''
        executables.load_modules_from_strings(*self._executables)
        self._complete = True

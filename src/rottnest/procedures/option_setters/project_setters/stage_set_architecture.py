'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.plugins import architectures

STAGE_TAG = 'set_architecture'

class SetArchitectureStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, architecture: str, *, tag=None, dependencies=None):
        self._complete = False
        self._architecture = architecture
        
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
        architectures.set_current_architecture(self._architecture)
        self._complete = True

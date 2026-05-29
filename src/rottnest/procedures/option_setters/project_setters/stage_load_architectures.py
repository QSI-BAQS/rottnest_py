'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from rottnest.plugins import architectures

STAGE_TAG = 'load_architectures'

class LoadArchitecturesStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, architectures: list, *, tag=None, dependencies=None):
        self._complete = False
        self._architectures = architectures
        
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
        architectures.load_modules_from_strings(*self._architectures)
        self._complete = True

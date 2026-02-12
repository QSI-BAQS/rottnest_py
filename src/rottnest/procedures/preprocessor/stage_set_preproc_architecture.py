'''
    Stage for hotswapping architectures
'''
from rottnest.plugins import architectures, executables
from rottnest.procedures import stage

STAGE_TAG = 'hotswap_architecture'

class SetPreprocessingArchitectureStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False

        self._backup = None
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Swaps the current rottnest architecture 
        '''
        # Todo replace with dynamic string
        self._backup = architectures.get_current_architecture()
        architectures.set_current_architecture(
            'Rz Counter' 
        )
        self._complete = True

    def get_original_architecture(self):
        '''
            Getter for the hotswapped architecture
        '''
        return self._backup

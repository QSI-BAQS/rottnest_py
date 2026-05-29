'''
    Stage for synchronising the architecture with the pool manager 
'''
from rottnest.procedures import stage
from rottnest.plugins import architectures

STAGE_TAG = 'synch_architecture'

class SynchroniseArchitectureStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False
        
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

        from rottnest.process_pool import get_pool

        pool = get_pool()
        arch = architectures.get_current_architecture()
        pool.set_architecture_module(arch.get_name())
        self._complete = True

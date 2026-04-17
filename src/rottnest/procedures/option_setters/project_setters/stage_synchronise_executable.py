'''
    Stage for synchronising the architecture with the pool manager 
'''
from rottnest.procedures import stage
from rottnest.plugins import executables 
from rottnest.process_pool import get_pool

STAGE_TAG = 'synch_architecture'

class SynchroniseExecutableStage(stage.RottnestCompilerStage):
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
        pool = get_pool()
        executable = executables.get_current_architecture()
        pool.set_executable_module(executable.get_name())

        params = executable.get_executable_params()
        pool.set_executable_params(params)

        self._complete = True

'''
    Stage for hotswapping architectures
'''
from rottnest.plugins import architectures, executables
from rottnest.procedures import stage


from rottnest.procedures.pool import procedure_pool

from . import stage_set_preproc_architecture


STAGE_TAG = 'reset_architecture'

class ResetPreprocessingArchitectureStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False

        # Execute depends on `get_original_architecture`
        # Which is bound to the environment by the 
        # stage_set_preproc_architecture stage
        if dependencies is None:
            dependencies = [
                stage_set_preproc_architecture.STAGE_TAG,
                procedure_pool.STAGE_TAG
            ] 


        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, environment):
        '''
            Resets a swapped architecture back to an
            original one            
        '''
        # Todo replace with dynamic string
        arch = environment.hotswap_architecture.get_original_architecture()
        
        architectures.set_current_option(
            arch.get_name()
        )
        self._complete = True

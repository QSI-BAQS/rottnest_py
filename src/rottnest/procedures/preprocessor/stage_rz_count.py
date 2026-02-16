'''
    Stage for hotswapping architectures
'''
from rottnest.plugins import architectures, executables
from rottnest.procedures import stage


from . import stage_reset_preproc_architecture


STAGE_TAG = 'get_rz_count'

class RzCountStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False
        self._rz_count = None

        if dependencies is None:
            dependencies = [
                stage_reset_preproc_architecture.STAGE_TAG
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
        # Get the composer
        rz_counts = environment.pool_procedure.get_results()

        # Acts over a map of tags and counts
        self._rz_count = sum(map(lambda x: x[1], rz_counts.items()))
        self._complete = True

    def __call__(self):
        '''
            Dispatches to get_rz_count
        '''
        return self.get_rz_count()

    def get_rz_count(self):
        '''
            Getter for the rz count
        '''
        return self._rz_count

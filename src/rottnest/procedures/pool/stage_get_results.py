from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus

from . import stage_synchronise

STAGE_TAG = 'get_results'

class GetResultsPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [stage_synchronise.STAGE_TAG] 
        self._complete = False
        self._results = None
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Synchronises and starts the workers
        '''
        pool = get_pool()
        self._results = pool.get_final_results()

    def __call__(self) -> "ResultsComposer":
        '''
            Wrapper for get_results
        '''
        return self.get_results()

    def get_results(self) -> "ResultsComposer":
        '''
            Getter for the results object
        '''
        return self._results

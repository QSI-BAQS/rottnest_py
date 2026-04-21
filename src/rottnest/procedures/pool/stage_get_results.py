from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool

from rottnest.process_pool.ipc_manager import IPCManager

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
            asynchronous=True
        )

    def execute(self, compiler_environment):
        '''
            Gets Final results
        '''
        self.poll(compiler_environment)

    def poll(self, compiler_environment):
        pool = get_pool()
        results = pool.get_final_results()
        if results is not IPCManager.NOT_FOUND:
            self._results = results
            self._complete = True

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

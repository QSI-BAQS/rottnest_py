from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool

from rottnest.process_pool.ipc_manager import IPCManager

STAGE_TAG = 'get_postprocessing_data'

class GetPostprocessingDataStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        if dependencies is None:
            dependencies = [] 
        self._complete = False
        self._results = None
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=True
        )

    def execute(self, compiler_environment):
        '''
            Gets postprocessing data
            Exec triggers an asynch call
        '''
        pool = get_pool()
        pool.get_postprocessing_data()

    def poll(self, compiler_environment):
        pool = get_pool()
        results = pool.poll_postprocessing_data()
        if results is not None:
            self._results = results
            self._complete = True

    def __call__(self) -> "ResultsComposer":
        '''
            Wrapper for get_results
        '''
        return self.get_postprocessing_data()

    def get_postprocessing_data(self) -> "ResultsComposer":
        '''
            Getter for the results object
        '''
        return self._results

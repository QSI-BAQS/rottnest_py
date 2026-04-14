from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus
from rottnest.server.app.application import RottnestApplication

from . import stage_start_pool


import json

STAGE_TAG = 'Run Pool'

class RunPoolStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, 
            reporting=True,
            tag=None,
            dependencies=None
        ):
        if dependencies is None:
            dependencies = [stage_start_pool.STAGE_TAG] 

        self._complete = False
        self._reporting = reporting

        super().__init__(tag=tag, dependencies=dependencies, asynchronous=True)

    def execute(self, compiler_environment):
        # TODO: load layout IDs
        pool = get_pool()
        pool.run_sequence([0])

    def poll(self, compiler_environment):
        '''
            Checks if the pool has finished
        '''
        
        pool = get_pool()
        status = pool.poll()
        self._complete = (
            status == PoolStatus.FINISHED
        )
        if self._reporting and not self._complete:
            app_instance = RottnestApplication.try_get_instance()
            if app_instance is not None:
                res = pool.get_results(blocking=False)
                stream = pool.get_results_stream()
                app_instance.websocket_result_write(res)
                app_instance.websocket_stream_write(stream)
            else:
                pool.flush_results_cache()
            
        else:
            # Not reporting, clear buffers
            pool.flush_results_cache()

    def complete(self):
        if self._reporting and self._complete: 
            app_instance = RottnestApplication.try_get_instance()
            if app_instance is not None:
                pool = get_pool()
                res = pool.get_final_results()
                app_instance.websocket_result_final_write(res)
                
        return self._complete

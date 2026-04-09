from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus
from rottnest.server.app.application import RottnestApplication

from . import stage_start_pool

from rottnest.protocol.net import Rottnest

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

        app = RottnestApplication.get_instance()
        wsock = app.get_websocket()

        status = pool.poll()
        self._complete = (
            status == PoolStatus.FINISHED
        )
        if self._reporting and not self._complete:
            res = pool.get_results(blocking=False)
            # stream = pool.get_results_stream()
            wsock.send(Rottnest\
                           .start_packet(Rottnest.data.run_result)\
                           .set_payload(res)\
                           .build())

            # NOTE: Results, graph_state info
            # wsock.send(json.dumps(list(stream))) # NOTE: stream of data?
        else:
            # Not reporting, clear buffers
            pool.flush_results_cache()

    def complete(self):
        if self._reporting and self._complete: 
            pool = get_pool()
            pool.get_final_results()
            # TODO: Flush final results to the websocket

        return self._complete

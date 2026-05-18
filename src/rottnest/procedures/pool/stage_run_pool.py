from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus
from . import stage_start_pool
from ..procedure_manager import MPSCChannelProvider, MPSC_LAYOUT_CHANNEL_TAG


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

        if self._reporting:
            mpsc_provider_instance: MPSCChannelProvider = MPSCChannelProvider.get_instance()
            self._writer, _mpsc_state = mpsc_provider_instance.get_writer(MPSC_LAYOUT_CHANNEL_TAG)

        super().__init__(tag=tag, dependencies=dependencies, asynchronous=True)

    def execute(self, compiler_environment):
        # TODO: load layout IDs
        pool = get_pool()
        pool.run_sequence([0])

    def poll(self, compiler_environment=None):
        '''
            Checks if the pool has finished
        '''        
        pool = get_pool()
        status = pool.poll()
        self._complete = (
            status == PoolStatus.FINISHED
        )

        if self._reporting and not self._complete:
            if self._writer is not None:
                stream = pool.get_results_stream()
                if len(stream) > 0:
                    self._writer.write_iter(stream)
            else:
                pool.flush_results_cache()
            
        else:
            # Not reporting, clear buffers
            pool.flush_results_cache()

    def complete(self):
        pool = get_pool()
        if self._reporting and self._complete: 
            if self._writer is not None:
                pool = get_pool()
                res = pool.get_final_results()
                self._writer.write(res)
            else:
                pool.flush_results_cache()
        else:
            pool.flush_results_cache()                
        return self._complete

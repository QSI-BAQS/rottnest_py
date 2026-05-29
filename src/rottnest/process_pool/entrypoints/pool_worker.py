'''
    Worker entrypoint wrapper
'''
from rottnest.process_pool.process_pool import ComputeUnitExecutorPool
from rottnest.process_pool.pool_manager import ComputeUnitExecutorPoolManager

from .entrypoint import ProcessEntrypoint
from . import process_type

from rottnest.process_pool.single_instantiation import block_instantiation


class PoolWorkerProcessHandler(ProcessEntrypoint)
    '''
        Entrypoint helper for the worker
    '''
    _PROCESS_TYPE = process_type.POOL_WORKER

    def blockers(self):
        '''
            Block other instantiators
        '''
        block_instantiation(
            ComputeUnitExecutorPoolManager,
            ComputeUnitExecutorPool
        )

    def main(self, worker, *args, **kwargs):
        worker.entrypoint(*args, **kwargs)

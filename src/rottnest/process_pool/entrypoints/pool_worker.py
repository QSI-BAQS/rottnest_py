'''
    Worker entrypoint wrapper
'''
from rottnest.process_pool.process_pool import ComputeUnitExecutorPool
from rottnest.process_pool.pool_manager import ComputeUnitExecutorPoolManager

from .entrypoint import ProcessEntrypoint
from . import process_type

from rottnest.process_pool.single_instantiation import block_instantiation


class PoolWorkerProcessHandler(ProcessEntrypoint):
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

    def main(self, *args, **kwargs):
        self.worker.entrypoint(*args, **kwargs)

    @classmethod
    def get_entrypoint(cls):
        '''
            Gets the worker entrypoint
        '''
        # Validation in super
        _ = super().get_entrypoint()

        # Load the entrypoing inline from singleton 
        # This avoids circulars between processes 
        from rottnest.plugins import architectures
        arch = architectures.get_current_option()
        return arch.get_worker_entrypoint()


def get_entrypoint(architecture = None):
    '''
        Dispatch function on base class method
    '''
    return PoolWorkerProcessHandler.get_entrypoint()

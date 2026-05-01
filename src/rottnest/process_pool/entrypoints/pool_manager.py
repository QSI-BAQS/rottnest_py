'''
    Worker entrypoint wrapper
'''
from rottnest.process_pool.process_pool import ComputeUnitExecutorPool
from rottnest.process_pool import pool_manager

from .entrypoint import ProcessEntrypoint
from . import process_type

from rottnest.process_pool.single_instantiation import block_instantiation


class PoolManagerProcessHandler(ProcessEntrypoint):
    '''
        Entrypoint helper for the worker
    '''
    _PROCESS_TYPE = process_type.POOL_MANAGER

    def blockers(self):
        '''
            Block other instantiators
        '''
        block_instantiation(
            ComputeUnitExecutorPool
        )

    def main(self, *args, **kwargs):
        '''
            Handover to the pool manager entrypoint
        '''
        pool_manager.entrypoint(*args, **kwargs)


def get_entrypoint():
    '''
        Dispatch function on base class method
    '''
    return PoolManagerProcessHandler.get_entrypoint()

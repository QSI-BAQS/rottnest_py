'''
    Worker entrypoint wrapper
'''
from rottnest.process_pool.process_pool import ComputeUnitExecutorPool

from rottnest.process_pool.single_instantiation import block_instantiation

from rottnest.process_pool.entrypoints.entrypoint import ProcessEntrypoint
from rottnest.process_pool.entrypoints import process_type


class PoolAPIHandler(ProcessEntrypoint):
    '''
        Entrypoint helper for the API handler 
        This is treated as an entrypoint as a process 
        context as it manages the spawning of the 
        manager.

        Using the same context handler we attempt to
        prevent duplicate spawns
    '''
    _PROCESS_TYPE = process_type.SERVER

    def __init__(self):
        '''
            Slightly different
        '''
        self._api = ComputeUnitExecutorPool()
        super().__init__(self)

    def get_api(self):
        '''
            Gets the API
        '''
        return self._api

    def blockers(self):
        '''
            Block other instantiators
        '''
        # Function import is intentional
        from rottnest.process_pool.pool_manager import ComputeUnitExecutorPoolManager

        block_instantiation(
            ComputeUnitExecutorPoolManager,
        )

    def main(self, *args, **kwargs):
        '''
            API doesn't really have a main loop
        '''

    @classmethod
    def entrypoint(cls):
        '''
            Spawn the object and perform context setup
        '''
        api_context = PoolAPIHandler()
        api_context.blockers()

        return api_context.get_api()


def entrypoint():
    '''
        Dispatch method
    '''
    return PoolAPIHandler.entrypoint()

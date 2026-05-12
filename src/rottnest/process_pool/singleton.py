'''
    Singleton reference for process pool object
'''

from rottnest.process_pool.process_pool import ComputeUnitExecutorPool
from rottnest.process_pool.entrypoints.pool_api import entrypoint as pool_entrypoint
from rottnest.process_pool.single_instantiation import block_instantiation

class PoolSingletonRef:
    '''
        Scoped reference wrapper for the process_pool
        singleton
    '''
    DO_NOT_INSTANTIATE = object()
    process_pool = None
    
    @classmethod
    def get_pool(cls):
        '''
            Getter for singleton reference'd class obj
            Triggers instantiation
        '''
        if cls.process_pool is None:
            cls.process_pool = pool_entrypoint()
        return cls.process_pool

    @classmethod
    def instantiate_pool(cls, *args, **kwargs):
        '''
            Instantiates and triggers the singleton
            reference to the process pool
        '''
        # TODO: Entrypoint
        if cls.process_pool is None: 
            cls.process_pool = ComputeUnitExecutorPool(*args, **kwargs)
            return cls.process_pool
        raise Exception("Pool Already Instantiated")

    @classmethod
    def terminate_pool(cls):
        '''
            Triggers pool shutdown with 
            all workers extinguished
        '''
        cls.get_pool().terminate()
       
    @classmethod 
    def block_pool(cls):
        '''
            Blocks the formation of a pool on this process
        '''
        # Check that a pool has not already been spawned
        assert cls.process_pool in [None, cls.DO_NOT_INSTANTIATE]
        
        # Block the pool
        cls.process_pool = cls.DO_NOT_INSTANTIATE

def get_pool():
    '''
        Dispatch for singleton reference 
    '''
    return PoolSingletonRef.get_pool()

def terminate_pool():
    '''
        Triggers the termination of the pool
    '''
    PoolSingletonRef.terminate_pool()

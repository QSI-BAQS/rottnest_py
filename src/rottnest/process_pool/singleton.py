'''
    Singleton reference for process pool object
'''

from rottnest.process_pool.process_pool import ComputeUnitExecutorPool

class PoolSingletonRef:
    '''
        Scoped reference wrapper for the process_pool
        singleton
    '''

    process_pool = None
    
    @classmethod
    def get_pool(cls):
        '''
            Getter for singleton reference'd class obj
            Triggers instantiation
        '''
        if cls.process_pool is None:
            cls.process_pool = ComputeUnitExecutorPool() 
        return cls.process_pool

    @classmethod
    def instantiate_pool(cls, *args, **kwargs):
        '''
            Instantiates and triggers the singleton
            reference to the process pool
        '''
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

def get_pool():
    '''
        Dispatch for singleton reference 
    '''
    return PoolSingletonRef.get_pool()

def instantiate_pool(*args, **kwargs):
    '''
        Dispatch for singleton reference
    '''
    return PoolSingletonRef.instantiate_pool(
        *args,
        **kwargs
    )

def terminate_pool():
    PoolSingletonRef.terminate_pool()

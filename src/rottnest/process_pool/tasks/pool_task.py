import abc

class PoolTask:
    '''
        Base pool task
    '''

    # Collector pattern
    _collector = set() 

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        PoolTask._collector.add(cls)

    @classmethod
    @abc.abstractmethod 
    def get_command(cls) -> str:
        '''
            Returns the command string 
        '''
 
    def __call__(self, pool_manager, *args, **kwargs):
        '''
        '''
        return self.task(pool_manager, *args, **kwargs)
    
    @abc.abstractmethod
    def task(self, pool_manager, *args, **kwargs):    
        '''
            Task runner
        '''

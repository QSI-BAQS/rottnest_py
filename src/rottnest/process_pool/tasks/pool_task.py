import abc

class PoolTask:
    '''
        Base pool task
    '''

    # Collector pattern
    _collector = {} 

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        PoolTask._collector[cls.get_command()] = cls

    @classmethod
    @abc.abstractmethod 
    def get_command(cls) -> str:
        '''
            Returns the command string 
        '''

    @classmethod
    def get_poll_key(cls) -> str:
        '''
            Optional
            For cases where the poll IPC header
            differs from the command
        '''
        return cls.get_command()

    @classmethod
    def get_finalise_key(cls) -> str:
        '''
            Optional
            For cases where the finalise IPC header 
            differs from the the command 
        '''
        return cls.get_command() 
 
    def __call__(self, pool_manager, *args, **kwargs):
        '''
        '''
        return self.task(pool_manager, *args, **kwargs)
    
    @abc.abstractmethod
    def task(self, pool_manager, *args, **kwargs):    
        '''
            Task runner
        '''

    def setup(self, *args, **kwargs):
        '''
            API side to the task
            Performs any setup needed
        '''

    @classmethod
    def submit(cls, *args):
        '''
            Simple submit wrapper
            Allows all tasks to be two sided
        '''
        return (
            cls.get_command(),
            args
        )

def get_pool_manager_tasks() -> dict:
    '''
        Triggers the task collector
    '''
    return {
        command: task() 
        for command, task in PoolTask._collector.items()
    }


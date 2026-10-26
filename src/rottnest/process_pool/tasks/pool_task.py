'''
    Base pool task
'''
import abc

def expect_response(fn):
    '''
        Behaviour check on whether a response is expected from this task 
    '''
    def _wrap(self, *args, **kwargs):
        '''
            Wrapper function
        '''
        result = fn(self, *args, **kwargs) 

        if self.EXPECT_RESPONSE and result is None:
            raise TypeError(f"{self.__class__.__name__} did not produce a response")

        elif (not self.EXPECT_RESPONSE) and (result is not None): 
            raise TypeError(f"{self.__class__.__name__} produced an unexpected response: {result}")

        # Passed checks
        return result
    # Return the wrapper
    return _wrap


class PoolTask:
    '''
        Base pool task
    '''
    EXPECT_RESPONSE = False

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
 
    @expect_response
    def __call__(self, pool_manager, *args, **kwargs):
        '''
        '''
        res = self.task(pool_manager, *args, **kwargs)
        return res
    
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
    def submit(cls, *args, **kwargs):
        '''
            Simple submit wrapper
            Allows all tasks to be two sided
        '''
        return (
            cls.get_command(),
            args,
            kwargs
        )

def get_pool_manager_tasks() -> dict:
    '''
        Triggers the task collector
    '''
    return {
        command: task() 
        for command, task in PoolTask._collector.items()
    }


'''
    Interface specification of the pool task
    This needs to be seprated due to init subclass shenanigans
'''
import abc

from rottnest.utils.interface import interface, interface_argcount, interface_argfilter

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

   

@interface
class PoolTaskInterface:
    '''
        Base pool task interface
        This object is separated to avoid collisions on 
        init subclass
    '''
    @classmethod
    @abc.abstractmethod 
    @interface_argcount
    def get_command(cls) -> str:
        '''
            Returns the command string 
        '''

    @classmethod
    @interface_argcount
    def get_poll_key(cls) -> str:
        '''
            Optional
            For cases where the poll IPC header
            differs from the command
        '''

    @classmethod
    @interface_argcount
    def get_finalise_key(cls) -> str:
        '''
            Optional
            For cases where the finalise IPC header 
            differs from the the command 
        '''
 
    @interface_argcount
    @expect_response
    def __call__(self, pool_manager, *args, **kwargs):
        '''
            Caller
        '''

    @abc.abstractmethod
    @interface_argfilter(lambda base, instance: base.__code__.co_argcount <= instance.__code__.co_argcount) 
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
 

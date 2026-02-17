'''
   Utility library for the debug monitor
   This is to ensure that the work is a little
   more opaque in this case where decorators are
   utilised and the monitor does not need to be setup
   or dragged in all the time 
'''
from rottnest.debug.monitor import DebugMonitor
from collections.abc import Callable
from typing import TypeVar

T = TypeVar('T')
I = TypeVar('I')

DEBUG_FN_UNKNOWN_STR = '<anonymous>'
DEBUG_MD_UNKNOWN_STR = '<unknown-module>'

def with_debug_log[**I, T](fn_to_wrap: Callable[I, T]) -> Callable[I, T]:
    '''
       Debug log is a decorator function that will
       wrap the  
    '''
    monitor = DebugMonitor.default() # Gets the singleton object here

    def _operation(*args: I.args, **kwargs: I.kwargs) -> T:
        '''
           Wrapper operation 
        '''
        callable_str = getattr(fn_to_wrap, '__name__', DEBUG_FN_UNKNOWN_STR)
        callable_mod = getattr(fn_to_wrap, '__module__', DEBUG_MD_UNKNOWN_STR)
        
        DebugMonitor.with_obj(callable_str, callable_mod)
        return fn_to_wrap(*args, **kwargs)


    if monitor.is_using_decorator():
        '''
           Returns the wrapped function 
        '''
        return _operation
    else:
        '''
          Will just return the function that isn't wrapped
        '''
        return fn_to_wrap
    

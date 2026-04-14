'''
   Utility library for the debug monitor
   This is to ensure that the work is a little
   more opaque in this case where decorators are
   utilised and the monitor does not need to be setup
   or dragged in all the time 
'''
from rottnest.debug.monitor import DebugMonitor
from collections.abc import Callable
from typing import TypeVar, ParamSpec
from os import getpid


T = TypeVar('T')
A = ParamSpec('A')


DEBUG_FN_UNKNOWN_STR = '<anonymous>'
DEBUG_MD_UNKNOWN_STR = '<unknown-module>'


def with_debug_log(*, msg: str | None = None, \
    verbose: bool = False) -> Callable:
    '''
       Debug log decorator that will allow for messages to be
       Specified here 
    '''


    def _with_debug(fn_to_wrap: Callable[A, T]) -> Callable[A, T]:
        '''
           Debug log is a decorator function that will
           wrap the function it is decorating
        '''
        monitor = DebugMonitor.default() # Gets the singleton object here
        callable_fn_name = getattr(fn_to_wrap, '__name__', DEBUG_FN_UNKNOWN_STR)
        callable_str = f"{callable_fn_name}(...)"
        callable_mod = getattr(fn_to_wrap, '__module__', DEBUG_MD_UNKNOWN_STR)

        if callable_mod == '__main__':
            getfile_name = getattr(fn_to_wrap, '__file__', None)
            if getfile_name is not None:
                callable_mod = f"{callable_mod}/{getfile_name}"
        
        message_str = callable_str
        if msg is not None:
            message_str = f"{callable_str}: {msg}"

        def _operation(*args: A.args, **kwargs: A.kwargs) -> T:
            '''
               Wrapper operation 
            '''
            message_to_print = message_str
            # NOTE: str() may be a bad assumption but likely to work
            # in most situations,
            #
            # Will use repr in this case
            if verbose:
                total_args = (*args, *kwargs)
                args_repr = repr(total_args)
                message_to_print = f"{callable_str}({args_repr}): {msg}"
                  
            DebugMonitor.with_obj(message_to_print, callable_mod)
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
    
    return _with_debug

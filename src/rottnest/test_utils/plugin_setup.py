'''
    Default plugin setup
    For tests that require plugin
    state
'''

from rottnest import test_utils
from rottnest.plugins import architectures, executables, error_budgets
from rottnest.test_utils.executable import SampleExecutable
from rottnest_preprocessor import PreprocessorArchitecture 
from rottnest_error_budgets import EvenDistribution

def setup_plugins_decorator(*args, **kwargs):
    '''
        Decorator wrapper
    '''
    def _wrap_caller(fn):
        '''
            Catches decorator arguments
        '''
        def _wrap_fn(*fn_args, **fn_kwargs):
            setup_plugins(*args, **kwargs)
            fn(*fn_args, **fn_kwargs)
        return _wrap_fn
    return _wrap_caller
         

def setup_plugins(
    executable = None,
    architecture = None,
    budget = None, 
):
    '''
        Simple plugin setup for
        test functions that 
        need this state
    '''
    if executable is None:
        executables.load_modules_from_strings(test_utils.__file__)

        executable = SampleExecutable.get_name()
    executables.set_current_option(executable)


    if architecture is None:
        architecture = PreprocessorArchitecture.get_name() 

    architectures.set_current_option(
        architecture
    )

    if budget is None:
        budget = EvenDistribution.get_name() 
    error_budgets.set_current_option(budget)


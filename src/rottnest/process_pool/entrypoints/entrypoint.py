'''
    Abstract base class wrapper for process entrypoints
    Handles spawn typing, setup and teardown of processes 
    
    This object doubles as a `handler` after instantatation
     which then manages the legal spawning of subprocess
     types
'''

import abc
from rottnest.process_pool.single_instantiation import SingleInstantiation

from . import process_type 

class ProcessEntrypoint(SingleInstantiation, abc.ABC):
    '''
        Single instantiating process entrypoint
        Should self-block on entry

        This is the abstract base type, implementations
        must specify a process type
    '''

    _instance = None
    _PROCESS_TYPE = None

    def __init__(self, *args, **kwargs):
        '''
            Simple handler workflow
        '''
        # Hook for handler
        ProcessEntrypoint._instance = self

        # Set context for current process
        process_type.set_type(self._PROCESS_TYPE)

        self._args = args
        self._kwargs = kwargs
    
    @classmethod
    def entrypoint(cls, *args, **kwargs):
        proc = cls(*args, **kwargs)
        proc.run()

    @classmethod
    def get_entrypoint(cls):
        '''
            Wraps spawn validation functions
            This asserts that the spawned
            process is a legal child of the current
            context
        ''' 
        handler = get_current_process_handler()

        if handler is not None:
            assert (
                process_type.get_type()
                ==
                handler.get_process_type()
            )
            process_type.validate(cls.get_process_type())
        return cls.entrypoint

    @classmethod
    def get_process_type(cls):
        '''
            Getter on process type
        '''
        return cls._PROCESS_TYPE

    def run(self):
        '''
            Main Runner for the process
        '''
        # Lifecycle of the process
        # This is bound in the init
        self.blockers()
        self.setup(*self._args, **self._kwargs)
        self.main(*self._args, **self._kwargs)
        self.finalise(*self._args, **self._kwargs)
        self.join()

    def __call__(self):
        '''
            Dispatch to runner
        '''
        return self.run()


    def blockers(self):
        '''
            Setup blocking methods on other objects
        '''

    def setup(self, *args, **kwargs):
        '''
            Setup the environment
        '''

    def main(self, *args, **kwargs):
        '''
            Main caller
        '''

    def finalise(self, *args, **kwargs):
        '''
            Any finalisation needed 
            This can do cleanup too
        '''

    def join(self, *args, **kwargs):
        '''
            Operations to kill the process
        '''

    @classmethod
    def get_handler(cls):
        '''
            Getter for process instance
        '''
        return cls._instance

def get_current_process_handler() -> ProcessEntrypoint:
    '''
        Getter for the current process handler
        Potentially useful debug method
    '''
    return ProcessEntrypoint.get_handler()

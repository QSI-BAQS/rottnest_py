'''
    Model wrapper functions for the process pool
'''

from rottnest.process_pool.process_pool import ComputeUnitExecutorPool 
from rottnest.process_pool.status_decorator import StatusTracked
from rottnest.process_pool import standalone

from rottnest.plugins import executables, architectures 

from rottnest.compute_units.layout_proxy import LayoutProxy


class ModelProcessPool(StatusTracked):
    '''
        Singleton process pool manager
        This handles a process pool object and wraps
        the appropriate calls 
    '''

    def __init__(self):
        '''
            Wrap a process pool
        '''
        self._pool = ComputeUnitExecutorPool()

    def get_status(self) -> str:
        '''
            Getter for status
            Defers to the pool status
        '''
        return self._pool.get_status()

    def set_status(self, status: str):
        '''
            Setter for status
        '''
        raise Exception("Cannot set status on the model object") 


    def update_loaded_modules(self):
        '''
            Triggers a synchronisation betwween the 
             singleton module managers and the pool 
             manager
        '''
        self._pool.synchronise_modules()

    def preprocess(self):
        '''
            Manages the preprocessing hooks
        '''
        pass

    def execute_standalone(self, compile_from_graph=True):
        executable = executables.get_current_executable()
        architecture = architectures.get_current_architecture()

        layout = LayoutProxy.get_layouts()

        # TODO: Use preprocessing results
        self.preprocess()

        # Force consumption of iterator
        result = standalone.compile(
            layout,
            executable,
            architecture,
            compile_from_graph=compile_from_graph
        )
        return result

    def synchronise(self):
        '''
            pool synchronises
        '''
        self._pool.synchronise_modules()
        self._pool.synch_from_singletons()

    def start(self):
        self._pool.start()

    def execute_pool(self):
        '''
            Launches the pool and executes 
        '''
        # Synchronise
        self.synchronise() 

        # Start the pool workers
        self.start()

        # Trigger a pre-processing pass
        self.preprocess()

        # Execute
        self.execute()
        
    def get_status(self):
        '''
            Getter for status
        '''
        return self._status

###
# Singleton Hook functions
##
process_pool = ModelProcessPool()

def run_standalone():
    pass

def run_pool():
    pass

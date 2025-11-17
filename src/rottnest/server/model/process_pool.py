'''

Model wrapper functions for the process pool

'''
from rottnest.process_pool.process_pool import ComputeUnit 

def status_update(status, post_status):
    '''
        Status update decorator factory
    '''
    def _wrap_fn(fn)
        '''
            Decorator wrapper
        '''
        def _wrap(self, *args, **kwargs):
            '''
                Decorator resolver
            '''
            self.set_status(status)
            result = fn(*args, **kwargs)
            self.set_status(post_status)
            return result
        return _wrap 
    return _wrap_fn


class PoolStatus:
    '''
        Namespacing class
        Not quite an ENUM
    '''
    UNSTARTED = 'UNSTARTED'
    IDLE = 'IDLE'
    SYNCHRONISING = 'SYNCHRONISING'
    PREPROCESSING = 'PREPROCESSING'
    EXECUTING = 'EXECUTING'



class ModelProcessPool():
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
        self._status = PoolStatus.UNSTARTED

    def set_status(self, status: str):
        '''
            Setter for status
        '''
        self._status = status

    @status_update(PoolStatus.SYNCHRONISING, PoolStatus.IDLE)
    def update_loaded_modules(self):
        '''
            Triggers a synchronisation betwween the 
             singleton module managers and the pool 
             manager
        '''
        self._pool.synchronise_modules()

    @status_update(PoolStatus.PREPROCESSING, PoolStatus.IDLE)
    def preprocess(self):
        '''
            Manages the preprocessing hooks
        '''
        pass

    def execute_standalone(self):
        executable = executables.get_current_executable()
        architecture = architectures.get_current_architecture()

        layout = example_region_obj

        # TODO: Use preprocessing results
        self.preprocess()

        # Force consumption of iterator
        result = standalone.compile(layout, executable, architecture)
        return result

    @status_update(PoolStatus.SYNCHRONISING, PoolStatus.IDLE)
    def synchronise(self):
        '''
            pool synchronises
        '''
        self._pool.synchronise_modules()
        self._pool.synch_from_singletons()

    @status_update(PoolStatus.STARTING, PoolStatus.IDLE)
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
        '''


###
# Singleton Hook functions
##

process_pool = _ProcessPool()

def run_standalone():



def run_pool():

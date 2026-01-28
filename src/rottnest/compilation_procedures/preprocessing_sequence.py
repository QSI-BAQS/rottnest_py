'''
    Handles the pre-processing pass
'''
from rottnest.executables.executable import RottnestExecutable 

from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus


RZ_COUNTER_ID = -1

class PreprocessPass(StatusTracked):
    '''
        Handles preprocessing
        Will likely be a template for the Rottnest `pass' structure
    '''

    def __init__(self):
        self._rz_counts = None
        self._rz_prec = None
        self._t_fidelity = None
        self._complete = False

        self._rz_complete = False
        self._t_complete = False
        self._pandora_complete = False

        # Gets a reference to the process pool singleton
        # By having a strict order of passes, this proxies ownership 
        # FE gains read access, and ability to subvert ownership  
        # only if it terminates the pass
        self.pool = get_pool() 

    def __call__(self):
        '''
            Dispatch binding for passes
        '''
        self.preprocess()

    def preprocess(self):
        '''
            Main invoker
        '''
        ...

    def poll(self):
        '''
            Polling method
            Used to force progress on asynch tasks
        '''
        if self.complete():
            return True
        

    def complete(self):
        '''
            Checks if the pass has completed
        '''
        if not self._complete:
            self._complete = self.t_complete()
        return self._complete
            
    def pandora_complete(self):
        '''
            Checks if the Pandora dispatch has completed
        '''
        if not self._pandora_complete:
            # TODO: Pandora polling  
            self._pandora_complete = True
        return self.pandora_complete: 

    def rz_complete(self):
        '''
            Checks if Rz precision calculations are complete
        '''
        if not self.pandora_complete():
            # Cannot complete, or indeed start until Pandora preprocessing has finished 
            return False

        if not self._rz_complete:
            # Poll
            if self.pool.poll() == PoolStatus.FINISHED:
                self._rz_complete = True
                self._rz_counts = self.pool.get_results()
                # TODO: Reset Pool
                self.rz_complete = True

        return self._rz_complete

    def t_complete(self):
        '''
            Checks if T fidelity calculations are complete
        '''
        if not self.rz_complete():
            # If Rz is not complete, don't worry about this yet
            return False
        return self._t_complete
        

    def preprocess_rz_prec(self, executable) -> int:
        '''
            Determines Rz Precisions
            Returns precision in bits
        '''
        prec = executable.get_rz_precision()
        if prec is RottnestExecutable.NO_ANALYTICAL_METHOD:  
           rz_counts = self.preprocess_rz_count()
        return prec
        

    def setup_rz_counter_layout():
        '''
            Setup a naive layout for Rz counting 
        '''
        if LayoutProxy.get_layout(RZ_COUNTER_ID) is None:
            memory_bound = 1000
            layout = {'mem_bound': memory_bound}
            LayoutProxy.add_layout_with_id(RZ_COUNTER_ID, layout)

    def preprocess_rz_count(self):
        '''
            Submits objects to the pool to perform an Rz count
            Does not handle the receipt of the result
        '''
        # Setup the pool
        self.pool.set_architecture_module(
            'Rz Counter' 
        )

        # Synch pool state 
        self.pool.synchronise()

        # Start workers
        self.pool.start_workers()
         
        # Run the sequence
        self.pool.run_sequence([RZ_COUNTER_ID])


    def preprocess_t_fid(self):
        ...

    def preprocess_pandora(self, executable):
        '''
            Passes objects to Pandora process for injection
        '''
        for key, pandora_obj in executable.precompute(): 
            ...

import abc

class RottnestExecutable(abc.ABC):
    '''
        Interface for Rottnest Executable objects 
    '''

    def precompute(self, *args, **kwargs):
        '''
            Precomputation of elements of
            the circuit 
        '''
        pass

    def  __call__(self, *args, **kwargs): 
        '''
            Dispatch for circuit generation 
        '''
        return self._generate_circuit(*args, **kwargs)

    def _generate_circuit(self):
        '''
           Abstract circuit generation method
        '''

    def get_parameters(self):
        '''
            Abstract method for returning tunable parameters  
        '''

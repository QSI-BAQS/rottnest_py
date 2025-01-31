'''
    Interrupts act as a pseudo message passing interface
    This allows us to pass information from the parsers down to the compiler as an instruction  
'''

NON_CACHING = object()

class _INTERRUPT:
    '''
        This is an interrupt class for chucking into streams of cirq moments 
        It iters into itself, and evaluates against itself 
        This means that it acts as a cirquit, a moment and an operator and can be caught
        at all three levels
    '''

    def __iter__(self):
        yield self 

    def decompose(self):
        '''
        Proxy function for pyliqtr parser 
        '''
        return iter(self)

    def __hash__(self):
        return id(INTERRUPT)

    def __eq__(self, other):
        return hash(self) == hash(other) 

    def cache_hash(self):
        '''
            Reserved value, None should never be hashed
        '''
        return NON_CACHING 

INTERRUPT = _INTERRUPT()

class CACHED(_INTERRUPT):

    REQUEST = object()
    START = object()
    END = object()

    '''
        This interrupt triggers if a result is cached 
    '''
    def __init__(
        self,
        cache_hash: bytes,
        request_type: object,
        non_participatory_qubits: int = 0,
        op = None
    ): 
        '''
Constructor for a cache interrupt
    :: cache_hash : bytes :: Hash of the cache request 
    :: request_type : object :: Enum-like of singleton instances acting as a message interface   
    :: non_participatory_qubits : int :: Number of qubits that will idle across this cache 
        '''
        self._cache_hash = cache_hash
        self.request_type = request_type
        self.op = op 
        self.fully_decomposed = True

    def cache_hash(self):
        return self._cache_hash

    def parse(self):
        pass

class _INTERRUPT:
    '''
        This is an interrupt class for chucking into streams of cirq moments 
        It iters into itself, and evaluates against itself 
        This means that it acts as a cirquit, a moment and an operator and can be caught
        at all three levels
    '''
    
    NON_CACHING = object()

    def __iter__(self):
        yield self 

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
    def __init__(self, cache_hash, request_type): 
        self._cache_hash = cache_hash
        self.request_type = request_type
        self.op = None
        self.fully_decomposed = True

    def cache_hash(self):
        return self._cache_hash

    def parse(self):
        pass

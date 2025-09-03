'''
    This class breaks out the compilation logic
    between the compilation manager and the 
    process pool manager 
'''

from rottnest.input_parsers.interrupt import INTERRUPT, CACHED


class CompilationManager:
    '''
        CompilationManager
        Handles compilation logic without reference
        to process pool logic
    '''

    def __init__():

        self.non_participatory_stack = [0]
        self.cache_hash_stack = [None]
        self.compute_unit_result_cache = defaultdict(dict)
        
        cache_processes = {
            CACHED.START: self._cache_start,
            CACHED.END: self._cache_start,
            CACHED.START: self._cache_start
        }


    def _cache_start(self, obj):
        '''
            Start cache entry
        '''
        self.cache_hash_stack.append(
            cache_obj.cache_hash()
        )
        self.non_participatory_stack.append(
            cache_obj.non_participatory_qubits        
        )


    def _cache_end(self, obj):
        '''
            Ends a cache entry
            It is expected that this matches the bottom 
             entry of the stack
        '''
        if self.cache_hash_stack[-1] != cache_obj.cache_hash():
            raise Exception(
                "Received unmatched cache_end in stream",
                cache_obj.cache_hash(),
                self.cache_hash_stack
            )
        
        cache_hash = self.cache_hash_stack.pop()
        non_participatory = self.non_participatory_stack.pop()


    def _cache_request(self, obj):
        '''
        '''
        # Process result from cache
        cache_hash = cache_obj.cache_hash()
        while not self.process_cache_request(
                cache_hash,
                np_qubits = cache_obj.non_participatory_qubits
            ):
            # Barrier until we can resolve this cache request
            self.process_result_elem()


    def process_elem_cache(self, obj) -> float:
        '''
            Processes a cache element
        '''
        cache_start = time.time()
        cache_obj = obj[0]

        # Process cache command
        if cache_obj.request_type is CACHED.START:
            self._cache_start(obj) 

        elif cache_obj.request_type is CACHED.END:
            self._cache_end(obj)

        elif cache_obj.request_type is CACHED.REQUEST:
            self._cache_request(obj) 

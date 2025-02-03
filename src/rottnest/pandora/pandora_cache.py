import pyLIQTR
from rottnest.pandora.pandora_sequencer import pandora_connection, PandoraSequencer


class PandoraCache:

    def __init__(self):
        self.hash_cache = {}
        self.class_cache = {}

    def in_cache(self, other, hash_obj=None): 
        obj = None
        if hash_obj is not None:
            obj = self.hash_cache.get(hash_obj, None)

        # Fallback to class cache 
        if obj is None:
            obj = self.class_cache.get(other, None)
        print(obj, other, hash_obj)
        return obj

    def add_class(self, class_obj, obj):
        self.class_cache[class_obj] = obj
       
    def add_hash(self, hash_obj, obj): 
        self.hash_cache[hash_obj] = obj


pandora_cache = PandoraCache() 

lcu = pyLIQTR.BlockEncodings.PauliStringLCU.PauliStringLCU
string = 'lcu'


# Skip if pandora is not enabled
if pandora_connection is not None:
    conn = pandora_connection.spawn('adjoint') 
    seq = PandoraSequencer(conn=conn)
    
    # TODO:
    # Blame google's properties for the strcmp
    pandora_cache.add_class('Adjoint', seq)

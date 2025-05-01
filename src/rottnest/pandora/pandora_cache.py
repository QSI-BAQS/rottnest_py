import pyLIQTR
from rottnest.pandora.pandora_sequencer import pandora_connection, PandoraSequencer
from rottnest.compute_units.architecture_proxy import ArchitectureProxy

from pyLIQTR.qubitization.qubitized_gates import QubitizedRotation, QubitizedReflection
from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare

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

def attach_class(db_name, class_obj):
    '''
        Attaches a class hook to the cache 
    '''
    class_str = class_obj.__name__ 
    conn = pandora_connection.spawn(db_name) 
    seq = PandoraSequencer(conn=conn)
    pandora_cache.add_class(class_str, seq)

def architecture_bind(arch_id: int):
    '''
        Extract pandora sequence parameters based on the architecture
    '''
    # Assumes deterministic generation / caching
    # TODO move to convex bound model in Pandora
    arch = ArchitectureProxy(arch_id)
    n_registers = arch.mem_bound()
    max_t = n_registers 
    max_d = n_registers
    batch_size = n_registers
    update_sequencer(max_t=max_t, max_d=max_d, batch_size=batch_size)

def update_sequencer(*args, **kwargs):
    '''
        Updates parameters for Pandora sequencers
    '''
    for seq in pandora_cache.hash_cache.values():
        seq.set_params(*args, **kwargs)

    for seq in pandora_cache.class_cache.values():
        seq.set_params(*args, **kwargs)


from pyLIQTR.qubitization.qubitized_gates import QubitizedRotation, QubitizedReflection
from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare
from qualtran._infra.adjoint import Adjoint

# Skip if pandora is not enabled
# This should be promoted to a module for each circuit that is to be constructed and run  
if pandora_connection is not None:

    attach_class('adjoint', Adjoint)
    #attach_class('lcu', PauliStringLCU)
    #attach_class('prepare_lcu', prepare_pauli_lcu)
    attach_class('qsp', QSP_Prepare)

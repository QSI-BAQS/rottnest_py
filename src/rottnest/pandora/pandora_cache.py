import base64

import pyLIQTR
from rottnest.pandora.pandora_sequencer import pandora_connection, PandoraSequencer
from rottnest.compute_units.architecture_proxy import ArchitectureProxy

from pyLIQTR.qubitization.qubitized_gates import QubitizedRotation, QubitizedReflection
from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare

from pandora.targeted_decomposition import add_cache_db


class PandoraCache:

    def __init__(self):
        self.hash_cache = {}
        self.class_cache = {}

    def in_cache(self, op):
        hsh = op._rottnest_hash()

        # Try the hash cache
        obj = self.hash_cache.get(hsh, None)

        # Fallback to class cache 
        if obj is None:
            obj = self.class_cache.get(type(op.gate), None)
        return obj


    def _pre_populate(self):
        # Load all existing entries
        pass

    def bind_class(self, op):

        table_name = self.db_table_name(op, hash_postfix=False)  

        # Add the operation to the pandora database
        conn = add_cache_db(pandora_connection, op, table_name)

        self.class_cache[type(op.gate)] = conn 

       
    def bind_hash(self, op): 

        table_name = self.db_table_name(op, hash_postfix=True)  
        hsh = op._rottnest_hash()

        # Add the operation to the pandora database
        conn = add_cache_db(pandora_connection, op, table_name)

        self.hash_cache[hsh] = conn 


    @staticmethod
    def db_table_name(op, *, hash_postfix=True):
        base_name = str(op.gate.__class__).split("'")[1].replace('.', '_')[:10]
        
        # Is the hash appended as a postfix? 
        if hash_postfix: 
            hsh = op._rottnest_hash()
            base_name += '_' + base64.b32encode(hsh).decode()[:-6]
        return base_name.lower() 

pandora_cache = PandoraCache() 

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
    pass
    #attach_class('adjoint', Adjoint)
    #attach_class('lcu', PauliStringLCU)
    #attach_class('prepare_lcu', prepare_pauli_lcu)
    #attach_class('qsp', QSP_Prepare)

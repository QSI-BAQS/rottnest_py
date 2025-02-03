import pyLIQTR
from rottnest.pandora.pandora_sequencer import pandora_connection, PandoraSequencer

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
    class_str = class_obj.__name__ 
    conn = pandora_connection.spawn(db_name) 
    seq = PandoraSequencer(conn=conn)
    pandora_cache.add_class(class_str, seq)

from pyLIQTR.qubitization.qubitized_gates import QubitizedRotation, QubitizedReflection
from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare
from qualtran._infra.adjoint import Adjoint

# Skip if pandora is not enabled
if pandora_connection is not None:

    attach_class('adjoint', Adjoint)
    #attach_class('lcu', PauliStringLCU)
    #attach_class('prepare_lcu', prepare_pauli_lcu)
    attach_class('qsp', QSP_Prepare)

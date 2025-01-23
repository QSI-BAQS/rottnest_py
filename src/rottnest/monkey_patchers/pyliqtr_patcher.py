import pyLIQTR
import pycrypto

hash_function_patchers = {


}

def qsvt_hash(operation):
    gate = operation.gate 

    # This should be bounded by 8 bytes
    base = type_hash(gate)

    # Assume this is bounded by 8 bytes
    num_qubits = gate.num_qubits



def type_hash(gate): 
    '''
        Only gates that share a type should hash identically
    '''
    return id(gate.__class__)



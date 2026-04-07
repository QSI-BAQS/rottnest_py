'''
    Hash functions for qubitised operations
'''
from Crypto.Hash import MD5
from pyLIQTR.qubitization.qubitized_gates import QubitizedRotation, QubitizedReflection

def qubitized_reflection_hash(_, operation):
    '''
    Qubitized reflection hash function
    '''
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate._n_controls.to_bytes(byteorder='little', length=4)
    ).digest()

def qubitized_rotation_hash(_, operation):
    '''
    Qubitized rotation hash function
    '''
    gate = operation.gate
    # Hashes over the rads and the number of qubits
    # Assumes that number of qubits <= (2 ** 32) - 1
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate.num_qubits().to_bytes(byteorder='little', length=4)
        + gate._rads.tobytes()
    ).digest()

TARGETS = {
    QubitizedRotation: qubitized_rotation_hash,
    QubitizedReflection: qubitized_reflection_hash,
}

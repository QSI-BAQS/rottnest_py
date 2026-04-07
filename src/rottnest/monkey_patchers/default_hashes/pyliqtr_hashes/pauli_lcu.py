'''
    Pauli LCU hashes
'''
from Crypto.Hash import MD5

from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu

def pauli_string_lcu_hash(_, operation):
    '''
    Hash function for lcu
    '''
    gate = operation.gate

    md5 = MD5.new(
            str(gate.__class__).encode('ascii')
        )

    # Read each LCU as an array of bytes
    # First element is a string, second is the coefficient as a float
    # String is ascii encoded and hashed, float is cast to struct and hashed as bytes
    for lcu in gate.PI.yield_PauliLCU_Info(return_as='arrays'):
        md5.update(np.array(lcu[0]).tobytes() + lcu[1].encode('ascii') + struct.pack('f', lcu[2]))

    return md5.digest()

def prepare_pauli_lcu_hash(_, operation):
    '''
    Prepare pauli lcu hash
    '''
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + np.array(gate._alphas).tobytes()
    ).digest()


TARGETS = {
    PauliStringLCU: pauli_string_lcu_hash,
    prepare_pauli_lcu: prepare_pauli_lcu_hash,
}

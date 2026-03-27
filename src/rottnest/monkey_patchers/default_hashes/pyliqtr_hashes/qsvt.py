'''
    QSVT hashes
'''
from Crypto.Hash import MD5
from pyLIQTR.qubitization.qsvt import QSVT_real_polynomial, QSVT_real_polynomial_sum

def qsvt_polynomial_sum_hash(_, operation):
    '''
    Hash function for qsvt polynomial sum function
    '''
    gate = operation.gate

    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate._phis_0.tobytes()
        + gate._phis_1.tobytes()
    ).digest()

def qsvt_real_polynomial_hash(_, operation):
    '''
    Hash function for real polynomial hash
    '''
    gate = operation.gate

    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate._phis.tobytes()
    ).digest()

TARGETS = {
    QSVT_real_polynomial_sum: qsvt_polynomial_sum_hash,
    QSVT_real_polynomial: qsvt_real_polynomial_hash
}

'''
    QSP functions
'''
from Crypto.Hash import MD5
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare

def qsp_prepare_hash(_, operation):
    '''
    Prepare qsp hash
    '''
    # TODO: Confirm alphas is sufficient
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + np.array(gate.alphas).tobytes()
    ).digest()

TARGETS = {
    QSP_Prepare: qsp_prepare_hash
}

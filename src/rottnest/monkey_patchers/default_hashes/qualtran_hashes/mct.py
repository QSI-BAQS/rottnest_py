'''
    Multi control bloq hashes
'''
from qualtran.bloqs.mcmt.multi_control_multi_target_pauli import MultiControlPauli
from qualtran.bloqs.mcmt.and_bloq import MultiAnd

def mcmt_pauli_prepare_hash(_, operation): 
    # TODO: Confirm alphas is sufficient
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + abs(operation.gate.cvs.__hash__()).to_bytes(byteorder='little', length=8)
        + id(operation.gate.target_gate).to_bytes(byteorder='little', length=8)
    ).digest()

def multi_and_hash(_, operation):
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + abs(operation.gate.cvs.__hash__()).to_bytes(byteorder='little', length=8)
    ).digest()

TARGETS = {
    MultiControlPauli: mcmt_pauli_prepare_hash,
    MultiAnd: multi_and_hash,
}

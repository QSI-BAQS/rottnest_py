'''
    LCU hash patchers
'''
from Crypto.Hash import MD5
from qualtran.bloqs.multiplexers.select_pauli_lcu import SelectPauliLCU

def select_pauli_lcu_hash(_, operation): 
    hsh = MD5.new(str(operation.gate.__class__).encode('ascii'))
    for i in operation.gate.select_unitaries:
        hsh.update(i.pauli_mask.tobytes())
        hsh.update(np.array([i.coefficient]).tobytes())
    return hsh.digest()

TARGETS = {
     SelectPauliLCU: select_pauli_lcu_hash
}

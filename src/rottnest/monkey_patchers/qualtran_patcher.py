'''
    Monkey Patchers for Qualtran objects 
    Hash functions are overloaded for caching
    Hashes must include the class name to avoid collisions
    on common integer sequences  
'''
import struct
from types import MethodType
import numpy as np

import qualtran 
from qualtran.bloqs.mcmt.multi_control_multi_target_pauli import MultiControlPauli
from qualtran.cirq_interop._bloq_to_cirq import BloqAsCirqGate 
from qualtran.bloqs.mcmt.and_bloq import MultiAnd
from qualtran._infra.adjoint import Adjoint
from qualtran.bloqs.multiplexers.select_pauli_lcu import SelectPauliLCU

from Crypto.Hash import MD5
import cirq


def mcmt_pauli_prepare_hash(_, operation): 
    # TODO: Confirm alphas is sufficient
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + operation.gate.cvs.__hash__().to_bytes(byteorder='little', length=8)
        + id(operation.gate.target_gate).to_bytes(byteorder='little', length=8)
    ).digest()

def multi_and_hash(_, operation):
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + operation.gate.cvs.__hash__().to_bytes(byteorder='little', length=8)
    ).digest()

def adjoint_hash(_, operation): 
    # TODO: Hash over cabaliser ops 
    hsh = MD5.new(str(operation.gate.__class__).encode('ascii'))
    nested = False
    for i in cirq.decompose(operation):
        # Concetenate hashes of hashable objects under the adjoint  
        # This lets our adjoint itself be cacheable up to cirq objects 
        # TODO: Add hashing functions to cirq objects 
        try:
            op_hash = i._rottnest_hash()
            if op_hash is not None:
                nested = True
                hsh.update(op_hash)
        except:
            pass
    if not nested:
        # Not nested, hash using the id of the object to guarantee uniqueness
        # As the resulting object is stored in the hash table this address won't be released
        # until the hash table is cleared
        hsh.update(
            id(operation).to_bytes(length=8, byteorder='little')
        )
    return hsh.digest()

def select_pauli_lcu_hash(_, operation): 
    hsh = MD5.new(str(operation.gate.__class__).encode('ascii'))
    for i in operation.gate.select_unitaries:
        hsh.update(i.pauli_mask.tobytes())
        hsh.update(np.array([i.coefficient]).tobytes())
    return hsh.digest()

class BloqWrapper:
    '''
        Tiny wrapper to remap bloqascirq objects
    '''
    def __init__(self, bloq):
        self.gate = bloq 

def bloq_as_cirq_hash(_, operation):
    wrapper = BloqWrapper(operation.gate.bloq)
    return hash_function_patchers[operation.gate.bloq.__class__](None, wrapper)

hash_function_patchers = {
    MultiControlPauli: mcmt_pauli_prepare_hash,
    MultiAnd: multi_and_hash,
    BloqAsCirqGate: bloq_as_cirq_hash,
    Adjoint: adjoint_hash,
    SelectPauliLCU: select_pauli_lcu_hash
}

def _monkey_patch():
    '''
        Injects the parsers into the cirq objects
        Linters will complain about this
    '''
    for gate_type, fn in hash_function_patchers.items():
        bound_method = MethodType(fn, gate_type)
        if gate_type is not None.__class__:
            # Some hash calculations take a while, caching is good
            gate_type._cached_rottnest_hash = None
            gate_type._rottnest_hash = bound_method

# Perform the monkey patching
# This will inject the _rottnest_hash method on import 
_monkey_patch()

'''
    Monkey Patchers for pyLIQTR objects 
    Hash functions are overloaded for caching
    Hashes must include the class name to avoid collisions
    on common integer sequences  
'''
import struct
from types import MethodType
import numpy as np

import pyLIQTR
from pyLIQTR.qubitization.qsvt import QSVT_real_polynomial, QSVT_real_polynomial_sum
from pyLIQTR.qubitization.qubitized_gates import QubitizedRotation, QubitizedReflection 
from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare 


from Crypto.Hash import MD5
import cirq


def qsvt_polynomial_sum_hash(_, operation):
    gate = operation.gate 

    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate._phis_0.tobytes()
        + gate._phis_1.tobytes()
    ).digest()

def qsvt_real_polynomial_hash(_, operation):
    gate = operation.gate 

    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate._phis.tobytes()
    ).digest()

def pauli_string_lcu_hash(_, operation):
    gate = operation.gate

    md5 = MD5.new(
            str(gate.__class__).encode('ascii')
        )
    
    for lcu in gate.PI.yield_PauliLCU_Info(return_as='arrays'):
        md5.update(np.array(lcu[0]).tobytes() + lcu[1].encode('ascii') + struct.pack('f', lcu[2]))

    return md5.digest() 

def qubitized_rotation_hash(_, operation):
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate.num_qubits().to_bytes(length=4)   
        + gate._rads.tobytes()
    ).digest()

def qubitized_reflection_hash(_, operation):
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + gate._n_controls.to_bytes(length=4)   
    ).digest()

def prepare_pauli_lcu_hash(_, operation): 
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + np.array(gate._alphas).tobytes()
    ).digest()


def qsp_prepare_hash(_, operation): 
    # TODO: Confirm alphas is sufficient
    gate = operation.gate
    return MD5.new(
        str(gate.__class__).encode('ascii')
        + np.array(gate.alphas).tobytes()
    ).digest()


hash_function_patchers = {
    QSVT_real_polynomial_sum: qsvt_polynomial_sum_hash, 
    QSVT_real_polynomial: qsvt_real_polynomial_hash,
    QubitizedRotation: qubitized_rotation_hash,
    QubitizedReflection: qubitized_reflection_hash,
    PauliStringLCU: pauli_string_lcu_hash,
    prepare_pauli_lcu: prepare_pauli_lcu_hash,
    QSP_Prepare: qsp_prepare_hash
}


def _rottnest_hash(self):
    if self.gate.__class__ in hash_function_patchers: 
        return self.gate._rottnest_hash(self) 
    # Non-hashing object
    return None 

def _monkey_patch():
    '''
        Injects the parsers into the cirq objects
        Linters will complain about this
    '''
    parse_method = MethodType(_rottnest_hash, cirq.ops.gate_operation.GateOperation)
    cirq.ops.gate_operation.GateOperation._rottnest_hash = _rottnest_hash 
    cirq.ops.controlled_operation.ControlledOperation._rottnest_hash = _rottnest_hash 

    for gate_type, fn in hash_function_patchers.items():
        bound_method = MethodType(fn, gate_type)
        if gate_type is not None.__class__:
            gate_type._rottnest_hash = bound_method 

# Perform the monkey patching
# This will inject the _rottnest_hash method on import 
_monkey_patch()

'''
    Monkey Patchers for pyLIQTR objects
    Hash functions are overloaded for caching
    Hashes must include the class name to avoid collisions
    on common integer sequences
'''
from types import MethodType
import cirq

from .decomposition_targets import rottnest_hash, get_hash_patcher 

from .default_hashes import pyliqtr_hashes

# Map of functions to classes to inject
hash_function_patchers = {} | pyliqtr_hashes.TARGETS 

def monkey_patch():
    '''
        Injects the parsers into the cirq objects
        Linters will complain about this
    '''
    parse_method = MethodType(rottnest_hash, cirq.ops.gate_operation.GateOperation)
    cirq.ops.gate_operation.GateOperation._rottnest_hash = rottnest_hash
    cirq.ops.controlled_operation.ControlledOperation._rottnest_hash = rottnest_hash

    cirq.ops.gate_operation.GateOperation._cached_rottnest_hash = None
    cirq.ops.controlled_operation.ControlledOperation._cached_rottnest_hash = None

    for gate_type, fn in hash_function_patchers.items():
        bound_method = MethodType(fn, gate_type)
        if gate_type is not None.__class__:
            # TODO Some hash calculations take a while, caching is good
            gate_type._rottnest_hash = bound_method

# Perform the monkey patching
# This will inject the _rottnest_hash method on import
monkey_patch()

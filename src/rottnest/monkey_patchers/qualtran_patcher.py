'''
    Monkey Patchers for Qualtran objects
    Hash functions are overloaded for caching
    Hashes must include the class name to avoid collisions
    on common integer sequences
'''
import cirq
import qualtran
import numpy

from types import MethodType

from Crypto.Hash import MD5

from qualtran.cirq_interop._bloq_to_cirq import BloqAsCirqGate

from .default_hashes import qualtran_hashes

# Special cased
class BloqWrapper:
    '''
        Tiny wrapper to remap bloqascirq objects
    '''
    def __init__(self, bloq):
        self.gate = bloq

def bloq_as_cirq_hash(_, operation):
    wrapper = BloqWrapper(operation.gate.bloq)
    return hash_function_patchers[operation.gate.bloq.__class__](None, wrapper)


def qualtran_free_as_cirq_op(self, qubit_manager, reg):
    '''
        Implements as_cirq_op for mapping qualtran Free to measure
    '''
    return (
        # Note that reg is variable size, which is supported
        # by cirq.measure
        cirq.measure(*reg),
        {'reg': numpy.array(reg)}
    )


hash_function_patchers = {
    BloqAsCirqGate: bloq_as_cirq_hash,
} | qualtran_hashes.TARGETS

def monkey_patch(patchers=None):
    '''
        Injects the parsers into the cirq objects
        Linters will complain about this
    '''
    if patchers is None:
        patchers = hash_function_patchers

    for gate_type, fn in patchers.items():
        bound_method = MethodType(fn, gate_type)
        if gate_type is not None.__class__:
            # Some hash calculations take a while, caching is good
            gate_type._cached_rottnest_hash = None
            gate_type._rottnest_hash = bound_method

    # Explicit patching of Free -> MeasureGate mapping
    qualtran.bloqs.bookkeeping.Free.as_cirq_op = qualtran_free_as_cirq_op

# Perform the monkey patching
# This will inject the _rottnest_hash method on import
monkey_patch()

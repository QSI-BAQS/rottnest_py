'''
    Adjoint Hash
'''
from Crypto.Hash import MD5
import cirq
from qualtran._infra.adjoint import Adjoint
from pyLIQTR.utils.circuit_decomposition import circuit_decompose_multi
from cirq import DecompositionContext, SimpleQubitManager

# Note: maybe this fails for things that aren't qualtran
#       (can you even get a non-bloq inside a qualtran Adjoint?)
shim_adjoint_sub = lambda sub: type(f"WrappedAdjointSubShim<{type(sub)}>", (), dict(gate=sub))()

def adjoint_hash(_, operation):
    hsh = MD5.new(str(operation.gate.__class__).encode('ascii'))
    nested = False

    adjoint_sub = operation.gate.subbloq
    wrapped_adjoint_sub = shim_adjoint_sub(adjoint_sub)

    try:
        # Assumes that bloqs are using _rottnest_hash(_, o) interface
        wrapped_hash = adjoint_sub._rottnest_hash(wrapped_adjoint_sub)
        if wrapped_hash is not None:
            hsh.update(wrapped_hash)
            return hsh.digest()
    # Non-cachable wrapped object - treat this as unique
    # (and so hash by id)
    except:
        pass

    hsh.update(id(operation).to_bytes(length=8, byteorder='little'))
    return hsh.digest()

TARGETS = {
    Adjoint: adjoint_hash
}

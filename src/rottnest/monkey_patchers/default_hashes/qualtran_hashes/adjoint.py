'''
    Adjoint Hash
'''
from Crypto.Hash import MD5
import cirq
from qualtran._infra.adjoint import Adjoint

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

TARGETS = {
    Adjoint: adjoint_hash
}

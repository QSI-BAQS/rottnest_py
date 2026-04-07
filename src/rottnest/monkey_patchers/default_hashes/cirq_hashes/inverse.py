'''
    Hash function for Inverse gates
'''
from cirq.ops.raw_types import _InverseCompositeGate
from Crypto.Hash import MD5

def inverse_composite_hash(_, operation):
    '''
    Inverse composite hash
    '''
    class InverseProxy():
        '''
        Doing this because some absolute pain at Cirq decided that things should be properties
        #TODO: Add anti-properties rant here
        '''
        def __init__(self, gate):
            self.gate = gate

    hsh = MD5.new(
        str(operation.gate.__class__).encode('ascii')
    )

    proxy = InverseProxy(operation.gate._original)
    hsh.update(operation.gate._original._rottnest_hash(proxy))
    return hsh.digest()

TARGETS = {
    _InverseCompositeGate: inverse_composite_hash
}

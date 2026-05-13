'''
    OnEach hash patcher
'''
from Crypto.Hash import MD5
from qualtran.bloqs.basic_gates.on_each import OnEach

def on_each_hash(_, operation):
    hsh = MD5.new(str(operation.gate.__class__).encode('ascii'))
    # Hash gate class being repeated as well
    hsh.update(str(operation.gate.gate.__class__).encode('ascii'))
    hsh.update(bytes(operation.gate.n))
    return hsh.digest()

TARGETS = {
    OnEach: on_each_hash
}

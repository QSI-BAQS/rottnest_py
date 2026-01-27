'''
    Utilities for directly interfacing with other quantum libraries
'''
import cirq
import qualtran.bloqs.basic_gates as qual_gates

from types import MethodType

from collections import Counter

def cirq_len(circuit):
    '''
        Determine the correct length for a given cirq circuit
        (accounting for internal wrapper sizes)
    '''
    lengths = {
        cirq.Rx: 3,
        cirq.Ry: 5
    }

    res = 0
    for moment in circuit.moments:
        for operation in moment:
            for t, v in lengths.items():
                if isinstance(operation.gate, t):
                    res += v
                    break
            else:
                res += 1

    return res


def qualtran_len(bloq):
    '''
        Determine the correct length for a given qualtran circuit
        (accounting for internal wrapper sizes)
    '''
    lengths = {
        qual_gates.Rx: 3,
        qual_gates.Ry: 5
    }

    res = 0
    for k, v in bloq.bloq_counts().items():
        for t, mult in lengths.items():
            if isinstance(k, t):
                res += v * mult
                break
        else:
            res += v

    return res


def cirq_n_rz(circuit):
    res = Counter()
    for moment in circuit.moments:
        for operation in moment:
            if (isinstance(operation.gate, (cirq.Rz, cirq.Ry, cirq.Rx)) or
                (isinstance(operation.gate, cirq.ZPowGate) and operation.gate.exponent == 0.25)):
                # NOTE : exponent 0.25 for a ZPow is a T (which maps to rz internally)
                res[operation.gate.exponent] += 1
            else:
                # This is a semi-ok check to see if the operation in question
                # is a composed (ie. not primitive) gate
                if hasattr(operation, "_decompose_"):
                    decomp = cirq.decompose(operation)
                    # |decomp| = 1 could imply primitive, as all primitives decompose to themselves
                    if len(decomp) == 1 and decomp[0].gate is operation.gate:
                        continue
                    res += cirq_n_rz(cirq.Circuit(*decomp))

    return res


def cirq_circuit_to_gate(circuit, n_qubits, hash_fn=None, name: str = 'CircuitAsGate'):
    '''
        Converts a circuit into an equivalent gate class for composition

        TODO: Allow providing a fixed qubit ordering (would make this usable for
        actual purposes?)
    '''
    def decompose(self, qubits):
        qubit_map = dict()
        qubit_idx = 0
        for moment in circuit.moments:
            for operation in moment:
                # Greedily allocate qubits from the circuit
                # to input qubits (destroys parameter ordering)
                for qb in operation.qubits:
                    if qb not in qubit_map.keys():
                        qubit_map[qb] = qubits[qubit_idx]
                        qubit_idx += 1
                yield operation.gate(*map(lambda v: qubit_map[v], operation.qubits))

    c = type(name, (cirq.Gate,), dict(
        name = name,
        _num_qubits_ = lambda *a, **ka: n_qubits,
        _circuit_diagram_info_ = lambda *a, **ka: [name] * n_qubits,
    ))

    def init(self):
        super(c, self)

    c.__init__ = MethodType(init, c)

    c._decompose_ = MethodType(decompose, c)

    if hash_fn is not None:
        c._rottnest_hash = MethodType(hash_fn, c)

    return c


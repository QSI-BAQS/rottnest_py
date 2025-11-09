'''
    Utilities for directly interfacing with other quantum libraries
'''
import cirq
import qualtran.bloqs.basic_gates as qual_gates

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

    return res

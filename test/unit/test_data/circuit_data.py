'''
    Declarative test circuits used by parsing tests
'''

import cirq
import math
import random

import qualtran.bloqs.basic_gates as qual_gates

from functools import reduce

# Ensure import works w/ both unittest and direct running
try:
    from utils.declarative_qualtran import build_bloq
except ModuleNotFoundError:
    from ..utils.declarative_qualtran import build_bloq

cirq_qubits = tuple(cirq.NamedQubit(str(x)) for x in range(100))

cirq_circuits = {
    # ---[ Trivial Single Gates ]---
    "single_x": cirq.Circuit(cirq.X(cirq_qubits[0])),
    "single_y": cirq.Circuit(cirq.Y(cirq_qubits[0])),
    "single_z": cirq.Circuit(cirq.Z(cirq_qubits[0])),
    "single_rx": cirq.Circuit(cirq.Rx(rads=0.0)(cirq_qubits[0])),
    "single_ry": cirq.Circuit(cirq.Ry(rads=0.0)(cirq_qubits[0])),
    "single_rz": cirq.Circuit(cirq.Rz(rads=0.0)(cirq_qubits[0])),
    "single_h": cirq.Circuit(cirq.H(cirq_qubits[0])),
    "single_s": cirq.Circuit(cirq.S(cirq_qubits[0])),
    "single_t": cirq.Circuit(cirq.T(cirq_qubits[0])),
    "single_cnot": cirq.Circuit(cirq.CNOT(cirq_qubits[0], cirq_qubits[1])),
    "single_cz": cirq.Circuit(cirq.CZ(cirq_qubits[0], cirq_qubits[1])),

    "h_x": cirq.Circuit(
        cirq.H(cirq_qubits[1]),
        cirq.X(cirq_qubits[0])
    ),

    "y_z_cnot": cirq.Circuit(
        cirq.Y(cirq_qubits[0]),
        cirq.Z(cirq_qubits[0]),
        cirq.CNOT(cirq_qubits[0], cirq_qubits[1])
    ),

    "hundred_x": cirq.Circuit(
        cirq.X(cirq_qubits[0]) for i in range(100)
    ),

    "h_measure": cirq.Circuit(
        cirq.H(cirq_qubits[0]),
        cirq.measure(cirq_qubits[0])
    ),

    # Toffoli
    "toffoli": cirq.Circuit(
        cirq.H(cirq_qubits[0]),
        cirq.CNOT(cirq_qubits[1], cirq_qubits[0]),
        cirq.Rz(rads=-math.pi / 4)(cirq_qubits[0]),
        cirq.CNOT(cirq_qubits[2], cirq_qubits[0]),
        cirq.Rz(rads=math.pi / 4)(cirq_qubits[0]),
        cirq.CNOT(cirq_qubits[2], cirq_qubits[0]),
        cirq.Rz(rads=-math.pi / 4)(cirq_qubits[0]),
        cirq.CNOT(cirq_qubits[1], cirq_qubits[0]),
        cirq.Rz(rads=math.pi / 4)(cirq_qubits[0]),
        cirq.Rz(rads=math.pi / 4)(cirq_qubits[2]),
        cirq.CNOT(cirq_qubits[1], cirq_qubits[2]),
        cirq.Rz(rads=math.pi / 4)(cirq_qubits[1]),
        cirq.Rz(rads=-math.pi / 4)(cirq_qubits[2]),
        cirq.CNOT(cirq_qubits[1], cirq_qubits[2]),
        cirq.H(cirq_qubits[0])
    ),

    # Massive parameterised toffoli
    "massive_toffoli": cirq.Circuit(
        reduce(lambda a, b: a + b,
            (
                [
                    cirq.H(qubit_0),
                    cirq.CNOT(qubit_1, qubit_0),
                    cirq.Rz(rads=-math.pi / 4)(qubit_0),
                    cirq.CNOT(qubit_2, qubit_0),
                    cirq.Rz(rads=math.pi / 4)(qubit_0),
                    cirq.CNOT(qubit_2, qubit_0),
                    cirq.Rz(rads=-math.pi / 4)(qubit_0),
                    cirq.CNOT(qubit_1, qubit_0),
                    cirq.Rz(rads=math.pi / 4)(qubit_0),
                    cirq.Rz(rads=math.pi / 4)(qubit_2),
                    cirq.CNOT(qubit_1, qubit_2),
                    cirq.Rz(rads=math.pi / 4)(qubit_1),
                    cirq.Rz(rads=-math.pi / 4)(qubit_2),
                    cirq.CNOT(qubit_1, qubit_2),
                    cirq.H(qubit_0)
                ] for qubit_0, qubit_1, qubit_2 in zip(cirq_qubits, cirq_qubits[1:], cirq_qubits[2:])
            )
        )
    ),

    "hundred_qubit_x": cirq.Circuit(
        cirq.X(cirq_qubits[n]) for n in range(100)
    )
}

qualtran_circuits = [
    # Note that the current Qualtran parsing uses the fact that `build_bloq` provides an object whose iterator
    # provides Cirq gates. This is NOT the standard function of an arbitrary Bloq
    build_bloq(
        registers = ('x',),
        gates = [
            (qual_gates.Hadamard(), {'q': 'x'})
        ]
    ),

    build_bloq(
        registers = ('x', 'y'),
        gates = [
            (qual_gates.Hadamard(), {'q': 'y'}),
            (qual_gates.XGate(), {'q': 'x'})
        ]
    ),

    build_bloq(
        registers = ('x', 'y'),
        gates = [
            (qual_gates.YGate(), {'q': 'x'}),
            (qual_gates.ZGate(), {'q': 'x'}),
            (qual_gates.CNOT(), {'ctrl': 'x', 'target': 'y'})
        ]
    ),

    build_bloq(
        registers = ('x',),
        gates = [
            (qual_gates.XGate(), {'q': 'x'}) for i in range(100)
        ]
    ),

    build_bloq(
        registers = ('x',),
        gates = [
            (qual_gates.Ry(0.0), {'q': 'x'}),
        ]
    ),

    build_bloq(
        registers = ('x', 'y', 'z'),
        gates = [
            (qual_gates.Hadamard(), {'q': 'x'}),
            (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'x'}),
            (qual_gates.Rz(-math.pi / 4), {'q': 'x'}),
            (qual_gates.CNOT(), {'ctrl': 'z', 'target': 'x'}),
            (qual_gates.Rz(math.pi / 4), {'q': 'x'}),
            (qual_gates.CNOT(), {'ctrl': 'z', 'target': 'x'}),
            (qual_gates.Rz(-math.pi / 4), {'q': 'x'}),
            (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'x'}),
            (qual_gates.Rz(math.pi / 4), {'q': 'x'}),
            (qual_gates.Rz(math.pi / 4), {'q': 'z'}),
            (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'z'}),
            (qual_gates.Rz(math.pi / 4), {'q': 'y'}),
            (qual_gates.Rz(-math.pi / 4), {'q': 'z'}),
            (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'z'}),
            (qual_gates.Hadamard(), {'q': 'z'})
        ]
    ),

    build_bloq(
        registers = tuple(str(i) for i in range(100)),
        gates = [
            (qual_gates.XGate(), {'q': str(i)}) for i in range(100)
        ]
    )
]

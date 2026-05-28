import unittest

import cirq
import math

from functools import reduce

from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.compute_units.sequencer import Sequencer
from rottnest.architecture_interface.rottnest_architecture import RottnestArchitecture

from rottnest.plugins import architectures

class MockParser():
    '''
        Wraps a cirq circuit in a parser interface
    '''
    def __init__(self, circuit):
        self.circuit = circuit

    def traverse(self):
        for moment in self.circuit:
            yield [moment,]

dummy_layout = { "mem_bound": 1000 }


class SequencerArchitecture(RottnestArchitecture):
    '''
        Dubious - acts as an architecture and a designer
    '''
    mem_bound = 1000

    @staticmethod
    def get_name():
        return "SequencerArchitecture"

    @staticmethod
    def composer(*a, **ka):
        return RottnestComposer

    @staticmethod
    def designer(*a, **ka):
        return SequencerArchitecture

    @staticmethod
    def get_mem_bound(layout):
        return SequencerArchitecture.mem_bound

    @staticmethod
    def set_mem_bound(n):
        SequencerArchitecture.mem_bound = n
        LayoutProxy.force_proxy_refresh()


class SequencerTest(unittest.TestCase):
    def setUp(self):
        self.cirq_qubits = [cirq.NamedQubit(str(x)) for x in range(100)]
        self.layout_id = 0
        LayoutProxy.add_layout_with_id(self.layout_id, dummy_layout)

        # Load a layout that provides a trivial mem bound
        architectures._force_set_current_architecture(SequencerArchitecture)

    def test_toffoli(self):
        SequencerArchitecture.set_mem_bound(1000)
        parser = MockParser(
            cirq.Circuit(
                cirq.H(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[0]),
                cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[2], self.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[2], self.cirq_qubits[0]),
                cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[2]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[2]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[1]),
                cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[2]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[2]),
                cirq.H(self.cirq_qubits[0])
            )
        )

        seq = Sequencer(self.layout_id)

        total_gates = 0
        total_rz = 0

        for cu in seq.sequence_pyliqtr(parser):
            total_gates += cu.n_gates
            total_rz += cu.n_rz_operations

        self.assertEqual(total_gates, 15)
        self.assertEqual(total_rz, 7)


    def test_toffoli_tiny_memory(self):
        SequencerArchitecture.set_mem_bound(100)
        parser = MockParser(
            cirq.Circuit(
                cirq.H(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[0]),
                cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[2], self.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[2], self.cirq_qubits[0]),
                cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[0]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[2]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[2]),
                cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[1]),
                cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[2]),
                cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[2]),
                cirq.H(self.cirq_qubits[0])
            )
        )

        seq = Sequencer(self.layout_id)

        total_gates = 0
        total_rz = 0

        for cu in seq.sequence_pyliqtr(parser):
            total_gates += cu.n_gates
            total_rz += cu.n_rz_operations

        self.assertEqual(total_gates, 15)
        self.assertEqual(total_rz, 7)


    def test_repeated_toffoli(self):
        SequencerArchitecture.set_mem_bound(1000)
        parser = MockParser(
            cirq.Circuit(reduce(lambda a, b: a + b,
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
                    ] for qubit_0, qubit_1, qubit_2 in zip(self.cirq_qubits, self.cirq_qubits[1:], self.cirq_qubits[2:])
                )
            ))
        )

        seq = Sequencer(self.layout_id)

        total_gates = 0
        total_rz = 0

        for cu in seq.sequence_pyliqtr(parser):
            total_gates += cu.n_gates
            total_rz += cu.n_rz_operations

        self.assertEqual(total_gates, 15 * (len(self.cirq_qubits) - 2))
        self.assertEqual(total_rz, 7 * (len(self.cirq_qubits) - 2))


    def test_repeated_toffoli_tiny_memory(self):
        SequencerArchitecture.set_mem_bound(100)
        parser = MockParser(
            cirq.Circuit(reduce(lambda a, b: a + b,
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
                    ] for qubit_0, qubit_1, qubit_2 in zip(self.cirq_qubits, self.cirq_qubits[1:], self.cirq_qubits[2:])
                )
            ))
        )

        seq = Sequencer(self.layout_id)

        total_gates = 0
        total_rz = 0

        for cu in seq.sequence_pyliqtr(parser):
            total_gates += cu.n_gates
            total_rz += cu.n_rz_operations

        self.assertEqual(total_gates, 15 * (len(self.cirq_qubits) - 2))
        self.assertEqual(total_rz, 7 * (len(self.cirq_qubits) - 2))


if __name__ == "__main__":
    unittest.main()

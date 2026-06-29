'''
    Ensures we can properly consume a multi-qubit MeasurementGate
'''

import unittest

import cirq

import cabaliser.gates as cabaliser_gates

from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.plugins import architectures

class MultiQubitMeasureTest(unittest.TestCase):
    def test_measure_count(self):
        architectures.set_current_architecture("Rz Counter")

        expected_measured_qubits = 32
        qb = [cirq.NamedQubit(str(x)) for x in range(expected_measured_qubits)]

        layout_id = 0
        LayoutProxy.add_layout_with_id(layout_id, { "mem_bound": 1000 })

        # measure all qubits w/ one MeasurementGate
        circuit = cirq.Circuit(cirq.measure(*qb))

        parser = PyliqtrParser(circuit)
        seq = Sequencer(layout_id)

        parser.parse()

        # number of measure gates
        n_cabaliser_measures = 0
        # qubits actually reported as measured (freed)
        measured_qubits = set()
        for cu in seq.sequence_pyliqtr(parser):
            measured_qubits.update(cu.get_measured_qubit_labels())

            for seq in cu.sequences:
                for gate in seq:
                    if gate.opcode == cabaliser_gates.MEAS:
                        n_cabaliser_measures += 1
                    else:
                        raise Exception("Got non-measure cabaliser op from sequence of a MeasurementGate")

        self.assertTrue(all(q in measured_qubits for q in qb))
        self.assertEqual(len(measured_qubits), expected_measured_qubits)
        self.assertEqual(n_cabaliser_measures, expected_measured_qubits)

if __name__ == "__main__":
    unittest.main()

import unittest
import cirq 
from rottnest.input_parsers import cirq_parser

from cabaliser import operation_sequence


class CirqTest(unittest.TestCase):

    def ghz(self, n_qubits=2):

        qubits = [cirq.NamedQubit(f'{i}') for i in range(n_qubits)] 

        c = cirq.Circuit()
        c.append(cirq.H(qubits[0]))
        for i in range(1, n_qubits):
            c.append(cirq.CNOT(qubits[i - 1], qubits[i]))
        return c  

    def test_ghz(self):

        n_qubits = 2
        circ = self.ghz(n_qubits=n_qubits)
        op = operation_sequence.OperationSequence(n_qubits)
        qubit_labels = cirq_parser.QubitLabelTracker()
        rz_tracker = cirq_parser.RzTagTracker() 
        return


if __name__ == '__main__':
    unittest.main()

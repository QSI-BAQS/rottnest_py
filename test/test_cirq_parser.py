import unittest
import time

import cirq 
from rottnest.input_parsers import cirq_parser

from cabaliser import operation_sequence
from cabaliser import widget



class CirqTest(unittest.TestCase):

    def ghz(self, n_qubits=2):

        qubits = [cirq.NamedQubit(f'{i}') for i in range(n_qubits)] 

        c = cirq.Circuit()
        c.append(cirq.H(qubits[0]))
        for i in range(1, n_qubits):
            c.append(cirq.CNOT(qubits[0], qubits[i]))
        return c  

    def exec_ghz(self, n_qubits=2):

        circ = self.ghz(n_qubits=n_qubits)
        op = operation_sequence.OperationSequence(n_qubits)
        qubit_labels = cirq_parser.QubitLabelTracker()
        rz_tracker = cirq_parser.RzTagTracker() 

        for moment in circ:
            for gate in moment:
                gate._parse_cabaliser(op, qubit_labels, rz_tracker) 
       
        wid = widget.Widget(n_qubits, n_qubits * 2 + 1);
        wid(op)

        wid.decompose()
        return
    
    def test_ghz(self):

        prev_msg_len = 0
        for i in range(2, 10000, 69):
            start = time.time()
            self.exec_ghz(n_qubits=i)
            end = time.time()
            msg = '\b' * prev_msg_len + f"\rExecuted: {i} in {end - start} seconds"
            print(msg , flush=False, end='')
            prev_msg_len = len(msg)


#n_qubits = 100 
#g = CirqTest() 
#
#circ = g.ghz(n_qubits=n_qubits)
#op = operation_sequence.OperationSequence(n_qubits)
#qubit_labels = cirq_parser.QubitLabelTracker()
#rz_tracker = cirq_parser.RzTagTracker() 
#
#for moment in circ:
#    for gate in moment:
#        gate._parse_cabaliser(op, qubit_labels, rz_tracker) 
#


if __name__ == '__main__':
    unittest.main()

import unittest
import time

import cirq 
from rottnest.input_parsers import cirq_parser

from factoring.rottnest_adder import Adder

from cabaliser import operation_sequence
from cabaliser import widget

class CirqTest(unittest.TestCase):
    
    def ghz(self, n_qubits=2):
        circ = Adder(n_qubits=n_qubits, stride=n_qubits, pandora=False) 
        return circ  

    def exec_ghz(self, circ, n_qubits=2, n_graph_qubits=8, seq_length=100):

        qubit_labels = cirq_parser.QubitLabelTracker()
        rz_tracker = cirq_parser.RzTagTracker() 

        parser = cirq_parser.CirqParser(seq_length) 

        wid = widget.Widget(n_qubits, n_graph_qubits);
        for op in parser.parse(circ):
            #raise Exception()
            wid(op)
        wid.decompose()
        return

    def test_ghz(self, n_qubits=3):
        n_graph_qubits = n_qubits * 40 

        circ = cirq.Circuit()
        for op in self.ghz(n_qubits=n_qubits)():
            circ.append(op)

        tot = 0
        t_min = float('inf') 
        t_max = 0
        for _ in range(5):
            start = time.time()
            self.exec_ghz(circ, n_qubits=n_qubits * 3 + 1, n_graph_qubits=n_graph_qubits)
            end = time.time()
            curr = end - start
            t_min = min(t_min, curr) 
            t_max = max(t_min, curr) 
            tot += curr 
           
        avg = tot / 5 
        msg = f"Executed: {n_qubits} in {avg} seconds pm {max(abs(avg - t_min), abs(avg - t_max))}"
        print(msg)
        #print(msg , flush=False, end='')
        #prev_msg_len = len(msg)


if __name__ == '__main__':
    time.sleep(0.1)
    print()
    tst = CirqTest()
    tst.test_ghz(n_qubits=2048)
    #unittest.main()

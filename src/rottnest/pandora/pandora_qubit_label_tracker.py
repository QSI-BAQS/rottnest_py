'''
    Qubit Label Tracker for Pandora 
    Unlike the regular qubit label tracker, this one tracks edges 
'''

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker


class PandoraQubitLabelTracker():

    def __init__(self):
        self._labels = dict()
        self.n_qubits = 0

    def __len__(self):
        return self.n_qubits

    def get(self, prev, nxt):
        qubit_idx = self._labels.get(prev, None) 
        if qubit_idx is None:
            qubit_idx = self.n_qubits
            self.n_qubits += 1 
            self._labels[nxt] = qubit_idx
            return qubit_idx

        self._labels[nxt] = qubit_idx        
        return qubit_idx 
       

    def get_single_qubit(self, gate):
        return self.get(gate.id * 10, gate.next_q1) 

    def get_two_qubit(self, gate):
        return (
            self.get(gate.id * 10, gate.next_q1),
            self.get(gate.id * 10 + 1, gate.next_q2)
    )
 
    def gets(self, *prev): 
        return tuple(map(self.get, prev))

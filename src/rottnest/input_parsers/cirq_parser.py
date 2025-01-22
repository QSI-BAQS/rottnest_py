from types import MethodType
from functools import partial

import cirq
import cabaliser.gates as cabaliser_gates
from cabaliser.operation_sequence import OperationSequence

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker

# Load and run the monkey patcher for cirq objects
from rottnest.monkey_patchers import cirq_patcher 
from rottnest.monkey_patchers.cirq_patcher import known_gates 

class CirqParser:
    '''
        Cirq Parser Object
    '''
    def __init__(
            self,
            sequence_length,
            rz_tracker=None
        ):
        self.sequence_length = sequence_length
        self._qubit_labels = QubitLabelTracker()

        if rz_tracker is None:
            rz_tracker = RzTagTracker()
        self._rz_tracker = rz_tracker 

    def __len__(self):
        '''
            Returns the amount of memory currently in use
        '''
        return len(self._qubit_labels) + self._rz_tracker.n_rz_gates 

    def reset_context(self):
        '''
            Resets local context
        '''
        prev_context = self._qubit_labels 
        self._qubit_labels = QubitLabelTracker()
        self._rz_tracker.reset()
        return prev_context

    def extract_context(self): 
        '''
        TODO: Tighten this 
        '''
        n_inputs = len(self._qubit_labels)
        n_rz_gates = self._rz_tracker.n_rz_gates 
        n_qubits = 2 * n_inputs + n_rz_gates 
        n_outputs = n_inputs 
        return n_inputs, n_qubits, n_outputs

    def parse(
        self,
        circ_iter: cirq.circuits.circuit.Circuit,
        widget = None
    ):

        op = OperationSequence(self.sequence_length)
        for moment in circ_iter:
            for operation in moment:
                if operation.gate._n_cabaliser_ops + len(op) > self.sequence_length:  
                    yield(op)
                    op = OperationSequence(self.sequence_length)
                operation.gate._parse_cabaliser(operation, op, self._qubit_labels, self._rz_tracker) 
        if len(op) > 0:
            yield op
        return

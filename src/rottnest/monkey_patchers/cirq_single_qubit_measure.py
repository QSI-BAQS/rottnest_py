'''
    Version of cirq's measure gate that only takes a single qubit

    We patch cirq measure to decompose to these, so that we can match cabaliser's
    single qubit measure as well
'''

import cirq

import cabaliser.gates as cabaliser_gates
from cabaliser.operation_sequence import OperationSequence

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker

class SingleQubitMeasure(cirq.Gate):
    '''
        Essentialy just a container for a qubit, identified by
        type

        Ensures that we can decompoes multi-qubit MeasurementGates into
        something that isn't another MeasurementGate, but can be
        identified and parsed to cabaliser
    '''
    def __init__(self):
        # cabaliser interface - this corresponds to one cabaliser measure
        self._n_cabaliser_ops = 1
        super(SingleQubitMeasure, self)

    def _num_qubits_(self):
        '''
            Required for cirq Gate type
        '''
        return 1

    def _parse_cabaliser(
        gate,    # this is the actual "self" (as a Gate)
        self,    # GateOperation instance of this Gate
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: RzTagTracker
    ):
        '''
            Required for mapping down to cabaliser
            This is typically patched into native cirq gates
            (see cirq_patcher.py), but can be implemented normally
            for a custom gate
        '''
        # Note that even though we unpack qubits, it is required to be
        # exactly one qubit
        operation_sequence.append(
            cabaliser_gates.MEAS,
            *qubit_labels.gets(*self.qubits)
        )

        qubit_labels.measure(*self.qubits)

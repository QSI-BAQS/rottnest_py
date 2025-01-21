'''
    cirq_parser
    Monkey patches cirq gate objects to inject
     a new _parse_cabaliser pseudo-slot method.
    Injects an identically named dispatch method
     in the gate_operation class.

    Provides an adapter class that ingests a
     cirq circuit as an iterable, carves out
     a graph-state compilable chunk as set by
     both memory and Rz count parameters and
     maintains iterator state.

    The patched method intentionally discards
     the self argument, and instead injects
     the gate_operation class, treating it as
     the class object. This method is used as
     gate_operations are compositional objects
     and the arguments of the operation are
     stored independently of the type of the
     gate.
    Monkey patching the gate type then loses
     the targets of the gate without also
     holding a reference to the gate_operation.
'''

from types import MethodType
from functools import partial

import cirq
import cabaliser.gates as cabaliser_gates
from cabaliser.operation_sequence import OperationSequence

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker

'''
Format for monkey patching:
    # gate parsing operation
    # number of qubits
    # number of gates
    # number of Rz gates
'''
def simple_operator(cabaliser_op):
    '''
    Simple operator wrapper
    Assumes a one-to-one correspondance between
     the underlying cirq object and the
     Cabaliser gate
    '''
    def _wrap(
        gate,  # Look...
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        operation_sequence.append(
            cabaliser_op,
            *qubit_labels.gets(*self.qubits)
        )
    return _wrap, 1

pauli_X = partial(simple_operator, cabaliser_gates.X)
pauli_Y = partial(simple_operator, cabaliser_gates.Y)
pauli_Z = partial(simple_operator, cabaliser_gates.Z)

measure = partial(simple_operator, cabaliser_gates.MEAS)


def h_pow():
    '''
        Hadamard adapter
    '''
    def _wrap(
        _,  # Look...
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        if self.gate.exponent == 1.0:
            operation_sequence.append(
                cabaliser_gates.H,
                *qubit_labels.gets(*self.qubits)
            )
        else:
            # TODO
            raise Exception("Not Implemented")
    return _wrap, 1


def X_to_Z(gate_fn):
    def _wrap(self, operation_sequence, qubit_labels, rz_tags): 
        operation_sequence.append(
            cabaliser_gates.H,
            *qubit_labels.gets(*self.qubits)
        )
        fn(self, operation_sequence, qubit_labels, rz_tags)
        operation_sequence.append(
            cabaliser_gates.H,
            *qubit_labels.gets(*self.qubits)
        )

def Y_to_Z(gate_fn):
    def _wrap(self, operation_sequence, qubit_labels, rz_tags): 
        operation_sequence.append(
            cabaliser_gates.S,
            *qubit_labels.gets(*self.qubits)
        )
        operation_sequence.append(
            cabaliser_gates.H,
            *qubit_labels.gets(*self.qubits)
        )
        fn(self, operation_sequence, qubit_labels, rz_tags)
        operation_sequence.append(
            cabaliser_gates.H,
            *qubit_labels.gets(*self.qubits)
        )
        operation_sequence.append(
            cabaliser_gates.Sdag,
            *qubit_labels.gets(*self.qubits)
        )

def x_pow():
    exponent_map = {
        1.0: _X_gate,  
        0.5: X_to_Z(_S_gate), 
        -0.5: X_to_Z(_Sdag_gate)
    }
    '''
       x_pow adapter
    '''
    def _wrap(
        _,  # Look...
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        if self.gate.exponent == 1.0:
            operation_sequence.append(
                cabaliser_gates.X,
                *qubit_labels.gets(*self.qubits)
            )
        else:
            # TODO
            raise Exception("Not Implemented")
    return _wrap, 1

def y_pow():
    '''
        Hadamard adapter
    '''
    def _wrap(
        _,  # Look...
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        # Direct comparison to 1 is bad
        if self.gate.exponent == 1.0:
            operation_sequence.append(
                cabaliser_gates.Y,
                *qubit_labels.gets(*self.qubits)
            )
        else:
            # TODO
            raise Exception("Not Implemented")
    return _wrap, 1


def _X_gate(self, operation_sequence, qubit_labels_rz_tags):
    operation_sequence.append(
            cabaliser_gates.X,
            *qubit_labels.gets(*self.qubits)
        )

def _Z_gate(self, operation_sequence, qubit_labels_rz_tags):
    operation_sequence.append(
            cabaliser_gates.Z,
            *qubit_labels.gets(*self.qubits)
        )

def _S_gate(self, operation_sequence, qubit_labels_rz_tags):
    operation_sequence.append(
            cabaliser_gates.S,
            *qubit_labels.gets(*self.qubits)
        )

def _Sdag_gate(self, operation_sequence, qubit_labels_rz_tags):
    operation_sequence.append(
            cabaliser_gates.Sdag,
            *qubit_labels.gets(*self.qubits)
        )

def _rz_gate(self, operation_sequence, qubit_labels, rz_tags):
        tag = rz_tags.get(self.gate.exponent, None)
        target = qubit_labels.gets(*self.qubits)[0]

        operation_sequence.append(
            cabaliser_gates.RZ,
            target, tag
        )

def z_pow():
    '''
        Hadamard adapter
    '''
    # Indirection table for pre-set angles
    exponent_map = {
        1.0: _Z_gate,  
        0.5: _S_gate, 
        -0.5: _Sdag_gate
    } 

    def _wrap(
        gate,
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        
        fn = exponent_map.get(gate.exponent, _rz_gate) 
        fn(self, operation_sequence, qubit_labels, rz_tags)

    return _wrap, 1

def rz():
    '''
        Rz gate
        # number of qubits
        # number of gates
        # number of Rz gates
    '''
    def _wrap(
        gate,  # Look...
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        tag = rz_tags.get(gate.exponent, None)
        target = qubit_labels.gets(*self.qubits)[0]

        operation_sequence.append(
            cabaliser_gates.RZ,
            target, tag
        )
    return _wrap, 1

def rx():
    '''
        Rx gate
        # number of qubits
        # number of gates
        # number of Rz gates
    '''
    def _wrap(
        gate,  # Look...
        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        tag = rz_tags(gate.angle, gate.eps)
        target = qubit_labels.gets(*self.qubits)[0]

        operation_sequence.append(
            cabaliser_gates.H,
            (target,)
        )

        operation_sequence.append(
            cabaliser_gates.RZ,
            (target, tag)
        )

        operation_sequence.append(
            cabaliser_gates.H,
            (target,)
        )

    return _wrap, 3


def ry():
    '''
        TODO: Confirm this transformation
        Ry gate
        # number of qubits
        # number of gates
        # number of Rz gates
    '''
    def _wrap(

        self,
        operation_sequence: OperationSequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        tag = rz_tags(self.angle, self.eps)
        target = qubit_labels.gets(self.qubits)[0]

        operation_sequence.append(
            cabaliser_gates.S,
            (target,)
        )

        operation_sequence.append(
            cabaliser_gates.H,
            (target,)
        )

        operation_sequence.append(
            cabaliser_gates.H,
            (target,)
        )

        operation_sequence.append(
            cabaliser_gates.RZ,
            (target, tag)
        )

        operation_sequence.append(
            cabaliser_gates.H,
            (target,)
        )

        operation_sequence.append(
            cabaliser_gates.Sdag,
            (target,)
        )

    return _wrap, 5


cx_pow = partial(simple_operator, cabaliser_gates.CNOT)
cz_pow = partial(simple_operator, cabaliser_gates.CZ)

def __blank(*args, **kwargs):
    return lambda x: x, 0 

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
        return len(self._qubit_labels)

    def reset_context(self):
        '''
            Resets local context
        '''
        prev_context = self._qubit_labels 
        self._qubit_labels = QubitLabelTracker()
        return prev_context

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

# Monkey patching list
# These will all be injected into their associated cirq class objects
known_gates = {
    cirq.ops.common_gates.HPowGate: h_pow,
    cirq.ops.common_gates.XPowGate: x_pow,
    cirq.ops.common_gates.YPowGate: y_pow,
    cirq.ops.common_gates.ZPowGate: z_pow,
    cirq.Rx: rx,
    cirq.Ry: ry,
    cirq.Rz: rz,
    cirq.ops.pauli_gates._PauliX: pauli_X,
    cirq.ops.pauli_gates._PauliY: pauli_Y,
    cirq.ops.pauli_gates._PauliZ: pauli_Z,
    cirq.ops.common_gates.CXPowGate: cx_pow,
    cirq.ops.common_gates.CZPowGate: cz_pow,
    cirq.T : rz, 
    cirq.ops.common_gates.MeasurementGate: measure, 
    cirq.ResetChannel: __blank,  # Delete from context
    cirq.ClassicallyControlledOperation: __blank, # Drop onto pauli tracker 
    None.__class__: __blank, # I don't know why the classical operations kick up nones like this
}

def _parse_cabaliser(self, *args, **kwargs):
    '''
        Dispatch method for invoking _parse_cabaliser in the
        associated operation 
    '''
    # self.gate hits the _ argument, while the second pass of self  
    # intentionally passes a reference from the gate_operation class to the
    # operation class   
    return self.gate._parse_cabaliser(self, *args, **kwargs)

def _monkey_patch():
    '''
        Injects the parsers into the cirq objects
        Linters will complain about this
    '''
    parse_method = MethodType(_parse_cabaliser, cirq.ops.gate_operation.GateOperation)
    cirq.ops.gate_operation.GateOperation._parse_cabaliser = parse_method 
    for gate_type, parser in known_gates.items():
        fn, n_gates = parser()
        bound_method = MethodType(fn, gate_type)

        if gate_type is not None.__class__:
            gate_type._parse_cabaliser = bound_method 
            gate_type._n_cabaliser_ops = n_gates

# Perform the monkey patching
_monkey_patch()

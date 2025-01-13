from functools import partial

import cirq
import cabaliser.gates as cabaliser_gates


class QubitLabelTracker:
    def __init__(self):
        self._labels = dict()

    def __getitem__(self, qubit_label):
        return self.get(qubit_label)

    def get(self, qubit_label): 
        '''
        Attempting to get a label 
        '''
        index = self._labels.get(qubit_label, None)
        if index is None: 
            index = len(self._labels)
            self._labels[qubit_label] = index
        return index

    def gets(self, *labels):
        return tuple(map(self.get, labels))

    def len(self):
        return len(self.labels)

    def __str__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


class RzTagTracker():
    '''
        Maps angles to tags
        TODO: This currently makes some very rough
        assumptions that no two gates will have
        the same angle and differing values of eps 
    '''
    def __init__(self):
        self._angles_to_tags = dict()
        self._tags_to_angles = list()
        self._eps = list()

    def __getitem__(self, tag):
        return self._tags_to_angles[tag]

    def get(self, angle, eps): 
        '''
        Attempting to get a label is bound to allocating one
        '''
        tag = self._angles_to_tags.get(angle, None)
        if tag is None: 
            tag = len(self.angles_to_tags)
            self._angles_to_tags[angle] = tag 
            self._tags_to_angles.append(angle)
            self._eps.append(eps)
        return tag 

    def gets(self, *angles):
        return tuple(map(self.get, angles))

    def len(self):
        return len(self.labels)

    def __str__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()





'''
Format for monkey patching:
    # gate parsing operation
    # number of qubits
    # number of gates
    # number of Rz gates 
'''
def simple_operator(cabaliser_op):
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):

        operation_sequence.append(
            cabaliser_op,
            *qubit_labels.gets(*self.qubits)
        )
    return _wrap, 1, 1, 0 
pauli_X = partial(simple_operator, cabaliser_gates.X)
pauli_Y = partial(simple_operator, cabaliser_gates.Y)
pauli_Z = partial(simple_operator, cabaliser_gates.Z)

def h_pow():
    '''
        Hadamard adapter
    '''
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
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
    return _wrap, 1, None, None 

def x_pow():
    '''
       x_pow adapter 
    '''
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
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
    return _wrap, 1, None, None 

def y_pow():
    '''
        Hadamard adapter
    '''
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
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
    return _wrap, 1, None, None 

def z_pow():
    '''
        Hadamard adapter
    '''
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        if self.gate.exponent == 1.0:
            operation_sequence.append(
                cabaliser_gates.Z,
                *qubit_labels.gets(*self.qubits)
            )
        else:
            # TODO
            raise Exception("Not Implemented")
    return _wrap, 1, None, None 

def rz():
    ''' 
        Rz gate
        # number of qubits
        # number of gates
        # number of Rz gates 
    '''
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        
        tag = rz_tags(self.angle, self.eps)
        target = qubit_labels.gets(*self.qubits)[0]

        operation_sequence.append(
            cabaliser_gates.RZ,
            (target, tag)
        )
    return _wrap, 1, 1, 1 

def rx():
    ''' 
        Rx gate
        # number of qubits
        # number of gates
        # number of Rz gates 
    '''
    def _wrap(
        _,  # Look... 
        self,
        operation_sequence,
        qubit_labels: QubitLabelTracker,
        rz_tags: QubitLabelTracker):
        
        tag = rz_tags(self.angle, self.eps)
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

    return _wrap, 1, 3, 1


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
        operation_sequence,
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

    return _wrap, 1, 5, 1


cx_pow = partial(simple_operator, cabaliser_gates.CNOT)
cz_pow = partial(simple_operator, cabaliser_gates.CZ)



def __blank(*args, **kwargs):
    return lambda x: x, 0, 0, 0 

class CirqParser:
    def parse(
        circ: cirq.circuits.circuit.Circuit,
        batch_width: int = 1000, # Unique qubits 
        batch_rz_len: int = 15000, # Rz gates
        batch_len: int = 100000 # Gates to batch
    ):
        tracked_labels = {} 
        for moment in circuit:
            for gate in moment: 
                pass

# Monkey patching list
# These will all be injected into their associated cirq # class objects
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
    cirq.ops.common_gates.MeasurementGate: __blank,
    cirq.ResetChannel: __blank,
    cirq.ClassicallyControlledOperation: __blank,
    None.__class__: __blank, # I don't know why this classical operations kick up nones like this
}

def _parse_cabaliser(self, *args, **kwargs):
    return self.gate._parse_cabaliser(self, *args, **kwargs)

def _monkey_patch():
    '''
        Injects the parsers into the cirq objects
    '''
    cirq.ops.gate_operation.GateOperation._parse_cabaliser = _parse_cabaliser
    for gate_type, parser in known_gates.items(): 
        if gate_type is not None.__class__:
            gate_type._parse_cabaliser = parser()[0]
_monkey_patch()

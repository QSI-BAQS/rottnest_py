'''
    Parser for cirq objects
    Maps to compute units of Cabaliser operations
'''
import cirq
from cabaliser.operation_sequence import OperationSequence

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.rz_tag_tracker import get_shared_rz_tracker 

# Load and run the monkey patcher for cirq objects
from rottnest.monkey_patchers import cirq_patcher
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING

from rottnest.monkey_patchers.cirq_patcher import known_gates

#from rottnest.pandora.pandora_sequencer import PandoraSequencer

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
            rz_tracker = get_shared_rz_tracker()
        self._rz_tracker = rz_tracker

    def __len__(self):
        '''
            Returns the amount of memory currently in use
        '''
        return len(self._qubit_labels) + self._rz_tracker.n_rz_gates

    def reset_context(self, *_sequences):
        '''
            Resets local context
        '''
        prev_context = self._qubit_labels

        self._qubit_labels = QubitLabelTracker()
        self._rz_tracker.reset()
        return prev_context

    def curr_mem(self):
        '''
            Current memory tracked by parser
        '''
        return len(self._qubit_labels) * 2 + self._rz_tracker.n_rz_gates

    def extract_context(self):
        '''
            Extracts the context of the parser to pass to the compute unit
        '''
        n_inputs = len(self._qubit_labels)
        n_rz_gates = self._rz_tracker.n_rz_gates
        n_qubits = 2 * n_inputs + n_rz_gates
        n_outputs = n_inputs
        rz_tracker = self._rz_tracker.to_dict()
        label_tracker = self._qubit_labels.to_dict()

        return n_inputs, n_qubits, n_outputs, rz_tracker, label_tracker

    def extract_rz_tracker(self) -> dict:
        '''
            Extracts terms from the Rz tracker for
            serialisation
        '''
        return self._rz_tracker.to_dict()

    def parse(
        self,
        circ_iter: cirq.circuits.circuit.Circuit,
        _widget = None
    ):
        '''
            Parses the object into interrupts and shims
        '''
        # This needs to be better
        # TODO: Fix cyclic dependency in pandora sequencer
        if isinstance(circ_iter, type(None)): #PandoraSequencer):
            yield from circ_iter.to_operation_sequence()
            return

        op = OperationSequence(max(self.sequence_length, cirq_patcher.MIN_SEQUENCE_LEN))

        for moment in circ_iter:
            for operation in moment:
                # TODO: Clean up the shim interface
                if isinstance(operation, tuple):
                    operation = operation[0]

                if operation == INTERRUPT:
                    if operation.cache_hash() is not NON_CACHING:
                        yield operation
                        continue
                    # Non Caching, immediately interrupt
                    yield operation
                    if len(op) > 0:
                        yield op
                        op = OperationSequence(max(self.sequence_length, cirq_patcher.MIN_SEQUENCE_LEN))
                    continue

                # Classically controlled gate
                if operation.gate is None:
                    operation = operation.without_classical_controls()

                # Append operation to next sequence
                if operation.gate._n_cabaliser_ops + len(op) > self.sequence_length:
                    yield op
                    op = OperationSequence(max(self.sequence_length, cirq_patcher.MIN_SEQUENCE_LEN))
                operation.gate._parse_cabaliser(operation, op, self._qubit_labels, self._rz_tracker)
        if len(op) > 0:
            yield op
        return


class CirqShim:
    '''
        Ducktyped proxy for wrapping gates into a circuit-like object
    '''

    def __init__(self):
        '''
            Shim constructor
        '''
        # List of gates object
        self._lst = []
        self.fully_decomposed = True
        self._parent_str = None

    def cache_hash(self):
        '''
            Shims are not cacheable and have no hash
        '''
        return None

    def append(self, obj):
        '''
            Adds an object to the shim
        '''
        self._lst.append(obj)

    def __iter__(self):
        '''
            Each gate appears as a moment
        '''
        for element in self._lst:
            yield (element,)

    def to_operation_sequence(self):
        '''
            Iterates over the elements in the shim
        '''
        return iter(self._lst)

    def traverse(self):
        '''
            Leaf object of dag, traversal is self
        '''
        yield self

    def flatten(self):
        '''
            Leaf object of dag, flatten is self
        '''
        return iter(self._lst)

    def __str__(self):
        '''
            String representation
        '''
        return f"Shim: {self._parent_str}"

    def set_parent(self, operation):
        '''
            Sets the parent of the node
        '''
        self._parent_str = str(operation.gate.__class__)

    def decompose(self):
        '''
            Leaf object of dag, decomposition is self
        '''
        return iter(self)

    def parse(self):
        '''
            Shims require no parsing
        '''

    def __len__(self):
        '''
            Operation in the shim
        '''
        return len(self._lst)

'''
    Wrapper object for Cabaliser sequences to be passed to a worker
'''

from cabaliser.widget import Widget

from rottnest.input_parsers.rz_tag_tracker import RzTagTracker
from rottnest.compute_units.layout_proxy import LayoutProxy


class ComputeUnit():
    '''
        Wrapper object for Cabaliser sequences to be passed to a worker
    '''

    counter = 0

    @classmethod
    def get_unit_id(cls):
        '''
            Unit ID generator
        '''
        unit_id = cls.counter
        cls.counter += 1
        return unit_id

    def __init__(
                self,
                layout_id: int,
                *,
                unit_id: str = None,
                mem_bound: int = None
            ):
        '''
            Constructor
        '''
        if unit_id is None:
            unit_id = ComputeUnit.get_unit_id()
        self.unit_id = unit_id

        # Should be equal to number of registers
        self.memory_bound = mem_bound

        self.layout_id = layout_id
        self.sequences = []

        # Context trackers
        self.n_inputs = 0
        self.n_outputs = 0
        self.n_qubits = 0

        self._qubit_labels = None
        self._rz_tracker_dict = None

        self.n_rz_operations = 0
        self.n_gates = 0

    def add_context(
            self,
            n_inputs: int,
            n_qubits: int,
            n_outputs: int,
            rz_tracker_dict: dict,
            qubit_labels: dict):
        '''
            Adds contextual information to the compute unit object
        '''
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.n_qubits = n_qubits
        self._rz_tracker_dict = rz_tracker_dict
        self._qubit_labels = qubit_labels

    def extract_rz_tracker(self):
        '''
            Wrapper around the rz_tracker constructor
        '''
        return RzTagTracker.from_dict(self._rz_tracker_dict)

    def curr_mem(self):
        '''
            Current widget memory
        '''
        return self.n_inputs * 2 + self.n_rz_operations

    def __iter__(self):
        return iter(self.sequences)

    def __len__(self):
        return len(self.sequences)

    def append(self, sequence):
        '''
            Adds a sequence to the compute unit
        '''
        self.n_gates += len(sequence)
        self.n_rz_operations += sequence.n_rz_operations
        self.sequences.append(sequence)

    def compile_graph_state(self):
        '''
            Compiles a graph state from the currently
             loaded sequences

            TODO: Setup context extraction decorator
        '''
        widget = Widget(
            self.n_inputs,
            self.n_qubits * 2 + 1
        )

        for op in self.sequences:
            widget(op)
        widget.decompose()
        return widget

    def get_qubit_labels(self):
        '''
            Returns the qubit labels
        '''
        return self._qubit_labels

    def export(self):
        '''
            Helper function
        '''
        return {
            'n_inputs': self.n_inputs,
            'n_outputs': self.n_outputs,
            'n_qubits': self.n_qubits,
        }

    def get_layout_json(self):
        '''
            Calls through the layout proxy singleton
            This is just a nice wrapper function
        '''
        return LayoutProxy.get_layout(self.layout_id)

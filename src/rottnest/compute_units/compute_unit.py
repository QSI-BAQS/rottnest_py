from cabaliser.widget import Widget
from rottnest.input_parsers.rz_tag_tracker import RzTagTracker

'''
Wrapper object for cabaliser sequences 
'''

counter = 0

class ComputeUnit(): 
    '''
        Wrapped object for sending
    '''
    def __init__(
                self,
                architecture,
                *,
                unit_id: str=None,
                mem_bound=None
            ):

        # TODO: mem bounds from architecture 
        global counter
        
        self.unit_id = counter 
        counter += 1

        self.memory_bound = mem_bound # Should be equal to number of registers
        self.architecture = architecture 
        self.sequences = list()
        
        # Context trackers
        self.n_inputs = 0
        self.n_outputs = 0
        self.n_qubits = 0
        
        self._rz_tracker_dict = None
         
        self.n_rz_operations = 0
        self.n_gates = 0
      
    def add_context(
            self,
            n_inputs: int,
            n_qubits: int,
            n_outputs: int,
            rz_tracker_dict: dict):
        '''
            Adds contextual information to the compute unit object
        '''
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.n_qubits = n_qubits
        self._rz_tracker_dict = rz_tracker_dict

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
        self.n_gates += len(sequence)
        self.n_rz_operations += sequence.n_rz_operations 
        self.sequences.append(sequence)

    def apply(self, widget): 
        # TODO remove
        for seq in self.sequences: 
            widget(seq)

    def compile_graph_state(self):
        '''
            TODO: Setup context extraction decorator
        '''
        widget = Widget(self.n_inputs, self.n_qubits * 2 + 1)
        for op in self.sequences:
            widget(op)
        widget.decompose()
        return widget

    def export(self):
        return {
            'n_inputs': self.n_inputs,
            'n_outputs': self.n_outputs,
            'n_qubits': self.n_qubits,
        }

    def get_architecture_json(self):
        return self.architecture

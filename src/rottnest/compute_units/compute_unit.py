from cabaliser.widget import Widget

'''
Wrapper object for cabaliser sequences 
'''

class ComputeUnit(): 
    '''
        Wrapped object for sending
    '''
    def __init__(self, architecture, unit_id: str=None):

        # TODO: mem bounds from architecture 
        
        self.unit_id = unit_id
        self.memory_bound = 100 
        self.architecture = architecture
        self.sequences = list()
        
        # Context trackers
        self.n_inputs = None
        self.n_outputs = None
        self.n_qubits = None
      
    def add_context(self, n_inputs, n_qubits, n_outputs):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.n_qubits = n_qubits
 
    def __len__(self):
        return len(self.sequences)
 
    def append(self, sequence):
        self.sequences.append(sequence)

    def apply(self, widget): 
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

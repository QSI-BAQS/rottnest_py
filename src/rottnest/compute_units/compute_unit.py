'''
Wrapper object for cabaliser sequences 
'''

class ComputeUnit(): 
    '''
        Wrapped object for sending
    '''
    def __init__(self, architecture):
        self.memory_bound = 0
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


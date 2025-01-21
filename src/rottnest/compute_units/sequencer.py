from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.cirq_parser import CirqParser

class Sequencer():
    '''
        Widget Sequencer
    '''
    def __init__(self,
            *architectures,
            sequence_length = 100,
            global_context = None
            ):
       
        # Map architectures to proxies 
        self._architecture_proxies = architectures
        self.priority_shim = [] 

        self.sequence_length = sequence_length

        if global_context is None:
            global_context = QubitLabelTracker()  

    def priority(self, gate, architecture):    
        pass

    def sequence_pyliqtr(self, parser):

        architecture_idx = 0

        # The choice of architecture should 
        # eventually be passed to a scheduler 
        compute_unit = ComputeUnit(self._architecture_proxies[architecture_idx]) 

        cirq_parser = CirqParser(self.sequence_length)

        for cirq_obj in parser.traverse():
            for op_seq in cirq_parser.parse(cirq_obj): 
                if op_seq.n_rz_operations + len(cirq_parser) > compute_unit.memory_bound:
                    yield compute_unit 

                    # Grab next architecture
                    # Eventually replace this with another scheduler
                    architecture_idx += 1 
                    architecture_idx %= len(self._architecture_proxies)

                    # Create a new compute unit
                    compute_unit = ComputeUnit(self._architecture_proxies[architecture_idx]) 

                    # Reset the context of the parser 
                    cirq_parser.reset_context() 
                # Add the offending sequence
                # TODO: This sequence may need splitting or similar special logic 
                # For now, so long as len(op_seq) is less than the number of qubits 
                # in register memory for the architecture this can't result in an illegal
                # allocation
                compute_unit.append(op_seq)
    
        if len(compute_unit) > 0: 
            yield compute_unit

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

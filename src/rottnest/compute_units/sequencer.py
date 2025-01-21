class Sequencer():
    '''
        Widget Sequencer
    '''
    def __init__(self,
            *architectures,
            sequence_length = 100
            ):
       
        # Map architectures to proxies 
        self._architecture_proxies = architectures
        self.priority_shim = [] 

        self.sequence_length = sequence_length

    def priority(self, gate, architecture):    
        pass

    def sequence_pyliqtr(self, parser):

        architecture_idx = 0
        compute_unit = ComputeUnit(self.architectures[architecture_idx]) 

        cirq_parser = CirqParser(self.sequence_length)

        for cirq_obj in parser.traverse():
            for op_seq in cirq_parser(cirq_obj): 
        
                if op_seq.n_rz_operations >    

                compute_unit.append(op_seq)
    
        if len(compute_unit) > 0: 
            yield compute_unit

class ComputeUnit(): 
    '''
        Wrapped object for sending
    '''
    def __init__(self, architecture):
        self.architecture = architecture
        self.sequences = list()
       
    def __len__(self):
        return len(sequences)
 
    def add_sequence(self, sequence):
        self.sequences.append(sequence)

    def apply(self, widget): 
        for seq in self.sequences: 
            widget(seq)

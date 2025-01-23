from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.cirq_parser import CirqParser
from rottnest.compute_units.compute_unit import ComputeUnit 

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

        print("Sequencing")
        for cirq_obj in parser.traverse():
            for op_seq in cirq_parser.parse(cirq_obj): 

                # TODO: inject RZ bounds here
                if op_seq.n_rz_operations + len(cirq_parser) > compute_unit.memory_bound:
                    local_context = cirq_parser.extract_context()
                    compute_unit.add_context(*local_context)
                    if len(compute_unit) > 0:
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
            local_context = cirq_parser.extract_context()
            compute_unit.add_context(*local_context)
            if local_context[0] > 0:
                yield compute_unit

from itertools import cycle

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.cirq_parser import CirqParser
from rottnest.input_parsers.pyliqtr_parser import INTERRUPT
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import ArchitectureProxy

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
        self._architecture_proxies = list(map(ArchitectureProxy, architectures))
        self.priority_shim = []

        self.sequence_length = sequence_length

        if global_context is None:
            global_context = QubitLabelTracker()

    def priority(self, gate, architecture):
        pass

    def sequence_pyliqtr(self, parser, compactness = 0.9):

        architecture_idx = 0

        # The choice of architecture should
        # eventually be passed to a scheduler

        architectures = cycle(self._architecture_proxies)    
 
        architecture = next(architectures) 
        compute_unit = ComputeUnit(architecture.to_json())
        cirq_parser = CirqParser(self.sequence_length)

        gate_count = 0

        for cirq_obj in parser.traverse():
            # Interrupt between cirq objects
            for op_seq in cirq_parser.parse(cirq_obj):

                # Interrupt encountered, force yield
                # This ensures that pyliqtr level objects compile to distinct  
                #  sequences of widgets
                # TODO: Option to skip interrupts to reduce widget count  
                if op_seq == INTERRUPT:
                    if len(compute_unit) > 0:
                        yield compute_unit

                    architecture = next(architectures)

                    # Create a new compute unit
                    compute_unit = ComputeUnit(architecture.to_json())

                    # Reset the context of the parser
                    cirq_parser.reset_context()
                    continue

                gate_count += len(op_seq)
                # Saturated memory bound 
                if op_seq.n_rz_operations + 2 * len(cirq_parser) > compute_unit.memory_bound * compactness :
                    compute_unit.append(op_seq)

                    local_context = cirq_parser.extract_context()
                    compute_unit.add_context(*local_context)
                    if len(compute_unit) > 0:
                        yield compute_unit

                    # Grab next architecture
                    # Eventually replace this with another scheduler
                    architecture = next(architectures)

                    # Create a new compute unit
                    compute_unit = ComputeUnit(architecture.to_json())

                    # Reset the context of the parser
                    cirq_parser.reset_context(op_seq)
                    cirq_parser.sequence_length = self.sequence_length 
                    continue

                # Add the  sequence
                compute_unit.append(op_seq)
               
                # Reduce sequence length 
                # This guarantees that hitting the compactness threshold doesn't run over the memory bound 
                cirq_parser.sequence_length = int(compactness * (compute_unit.memory_bound - (op_seq.n_rz_operations) + 2 * len(cirq_parser))) 

        if len(compute_unit) > 0:
            local_context = cirq_parser.extract_context()
            compute_unit.add_context(*local_context)
            if local_context[0] > 0:
                yield compute_unit
        print("Gate Count:", gate_count)

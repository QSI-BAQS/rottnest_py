from itertools import cycle

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.cirq_parser import CirqParser
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING
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

        # TODO: Update the length dynamically  
        self.sequence_length = self._architecture_proxies[0].mem_bound()

        if global_context is None:
            global_context = QubitLabelTracker()

    def priority(self, gate, architecture):
        pass

    def sequence_pyliqtr(self, parser, compactness = 0.9):

        architecture_idx = 0

        architectures = cycle(self._architecture_proxies)    
 
        architecture = next(architectures) 
        compute_unit = ComputeUnit(architecture.to_json(), mem_bound=architecture.mem_bound())
        print(compute_unit.memory_bound)

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
                    # Cache interrupt
                    if op_seq.cache_hash() is not NON_CACHING:
                        yield op_seq
                        continue

                    if len(compute_unit.sequences) > 0:
                        local_context = cirq_parser.extract_context()
                        compute_unit.add_context(*local_context)
                        yield compute_unit

                        architecture = next(architectures)
                        # Create a new compute unit
                        compute_unit = ComputeUnit(architecture.to_json(), mem_bound=architecture.mem_bound())

                        # Reset the context of the parser
                        cirq_parser.reset_context(op_seq)
                        cirq_parser.sequence_length = self.sequence_length 
                        continue

                gate_count += len(op_seq)

                curr_memory = compute_unit.n_rz_operations + 2 * len(cirq_parser)
                # This doesn't track additional qubit allocations
                if curr_memory + op_seq.n_rz_operations > compute_unit.memory_bound * compactness:
                    compute_unit.append(op_seq)

                    local_context = cirq_parser.extract_context()
                    compute_unit.add_context(*local_context)
                    if len(compute_unit) > 0:
                        yield compute_unit

                    # Grab next architecture
                    # Eventually replace this with another scheduler
                    architecture = next(architectures)

                    # Create a new compute unit
                    compute_unit = ComputeUnit(architecture.to_json(), mem_bound=architecture.mem_bound())

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

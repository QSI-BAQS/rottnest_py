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

    def sequence_pyliqtr(self, parser):

        architecture_idx = 0

        # The choice of architecture should
        # eventually be passed to a scheduler

        architectures = cycle(self._architecture_proxies)    
 
        architecture = next(architectures) 
        compute_unit = ComputeUnit(architecture.to_json())
        cirq_parser = CirqParser(self.sequence_length)

        print("Sequencing")
        interrupt = INTERRUPT()
        for cirq_obj in parser.traverse():
            # Interrupt between cirq objects
            for op_seq in cirq_parser.parse(cirq_obj):

                # Interrupt encountered, force yield
                if op_seq == interrupt:
                    if len(compute_unit) > 0:
                        yield compute_unit

                    architecture = next(architectures)

                    # Create a new compute unit
                    compute_unit = ComputeUnit(architecture.to_json())

                    # Reset the context of the parser
                    cirq_parser.reset_context()
                    continue

                # TODO: inject RZ bounds here
                if op_seq.n_rz_operations + 2 * len(cirq_parser) > compute_unit.memory_bound:
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
                    print("Roll-forward")
                    # TODO: Better sequence splitting logic here!
                    continue
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

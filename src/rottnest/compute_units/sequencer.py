from itertools import cycle

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.cirq_parser import CirqParser
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.architecture_proxy import ArchitectureProxy
from rottnest.monkey_patchers.cirq_patcher import MIN_SEQUENCE_LENGTH

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

        # Worst case: CNOT operation on a pair of new qubits induces two teleportations (2x2)
        self.sequence_length = int(self._architecture_proxies[0].mem_bound() * 0.8) // 4

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
        # Discard lingering global context
        cirq_parser.reset_context()

        yield_unit = False

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
                        yield_unit = True
                    else:
                        continue
                else:
                    if cirq_parser.sequence_length <= MIN_SEQUENCE_LENGTH:
                        compute_unit.append(op_seq)
                        yield_unit = True
                        # Consume op_seq so it isn't also added to the next unit
                        op_seq = None
                    elif cirq_parser.curr_mem() > compute_unit.memory_bound - MIN_SEQUENCE_LENGTH:
                        yield_unit = True

                if yield_unit:
                    local_context = cirq_parser.extract_context()
                    compute_unit.add_context(*local_context)
                    yield compute_unit

                    yield_unit = False

                    architecture = next(architectures)
                    compute_unit = ComputeUnit(architecture.to_json(), mem_bound=architecture.mem_bound())
                    cirq_parser.reset_context(op_seq)
                    cirq_parser.sequence_length = self.sequence_length

                if op_seq is not None:
                    gate_count += len(op_seq)

                    compute_unit.append(op_seq)
                    cirq_parser.sequence_length = (self.sequence_length * 4 - cirq_parser.curr_mem()) // 4

        if len(compute_unit) > 0:
            local_context = cirq_parser.extract_context()
            compute_unit.add_context(*local_context)
            if local_context[0] > 0:
                yield compute_unit

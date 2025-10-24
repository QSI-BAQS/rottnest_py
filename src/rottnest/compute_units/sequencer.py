from itertools import cycle

from rottnest.input_parsers.qubit_label_tracker import QubitLabelTracker
from rottnest.input_parsers.cirq_parser import CirqParser
from rottnest.input_parsers.interrupt import INTERRUPT, NON_CACHING
from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.monkey_patchers.cirq_patcher import MIN_SEQUENCE_LEN

class Sequencer():
    '''
        Widget Sequencer
    '''
    def __init__(self,
            *layouts,
            sequence_length = 100,
            global_context = None,
            composer = None
            ):

        # Map layouts to proxies
        # TODO: determine ownership of this vs ids

        #print("Layouts: ", layouts)
        #print("", )
        self._layout_proxies = list(map(LayoutProxy, layouts))
        self.priority_shim = []

        # Worst case: Rz operation on a new qubit induces an input, graph state and
        # teleported qubit
        self.sequence_length = int(self._layout_proxies[0].mem_bound() * 0.8) // 3

        if global_context is None:
            global_context = QubitLabelTracker()

        self.composer = composer

    def priority(self, gate, layout):
        pass


    def sequence_pyliqtr(self, parser):
        '''
            Performs sequencing over a PyliqtrParser, providing an iterator yielding
            bounded-size ComputeUnits

            IN:
                parser [PyliqtrParser]
                    The parser to acquire operation sequences from
                    Must have already had `parse` called on it, so that it can
                    be traversed


            OUT: [Iterator<ComputeUnits>]
                A series of ComputeUnits holding sequential components of the overall
                object being parsed
        '''
        # Determine if layouts are being drawn from a fixed pool (explicitly passed
        # and loaded via the LayoutProxy) or from a composer
        if self.composer is None:
            layout_generator = cycle(self._layout_proxies)
        else:
            # Delegate to the composer
            layout_generator = self.composer.layout_sequence_generator()

        curr_layout = next(layout_generator)

        cirq_parser = CirqParser(self.sequence_length)
        # Ensure any lingering global context is discarded
        cirq_parser.reset_context()

        compute_unit = ComputeUnit(curr_layout.layout_id, mem_bound=curr_layout.mem_bound())

        yield_unit = False

        # Parser drops down to cirq
        for cirq_object in parser.traverse():
            op_iter = cirq_parser.parse(cirq_object)
            op_seq = next(op_iter, None)
            # At present, this could actually be a for loop (as there is no path where
            # we don't get the next op_seq)
            while op_seq is not None:
                # Interrupt forces an early yield to force distinct Pyliqtr sequences
                if op_seq == INTERRUPT:
                    if op_seq.cache_hash() is not NON_CACHING:
                        # directly provide op_seq object, then grab the next one
                        # (ignoring anything else we would've done with a regular op_seq)
                        yield op_seq
                        op_seq = next(op_iter, None)
                        continue
                    # The sequence is NON_CACHING, and we have at least one sequence in the
                    # compute unit - this means we need to provide that compute unit
                    elif len(compute_unit.sequences) > 0:
                        yield_unit = True
                else:
                    # If our parser doesn't have enough room left for the minimal sequence,
                    # or is going to hit the memory bound for a compute unit, yield the unit
                    if (cirq_parser.sequence_length <= MIN_SEQUENCE_LEN or
                        cirq_parser.curr_mem() + 3 * op_seq.n_rz_operations + len(op_seq) > compute_unit.memory_bound - MIN_SEQUENCE_LEN):
                        yield_unit = True

                if yield_unit:
                    # TODO : This context is actually interleaved in a pretty nasty way if we get an op_seq
                    # that we can't fit or that is below the minimum. Need to fix at the cirq_parser level
                    local_ctx = cirq_parser.extract_context()
                    compute_unit.add_context(*local_ctx)
                    yield compute_unit

                    yield_unit = False

                    # Prepare a new unit on the next layout and reset the context
                    curr_layout = next(layout_generator)
                    compute_unit = ComputeUnit(curr_layout.layout_id, mem_bound=curr_layout.mem_bound())
                    cirq_parser.reset_context(op_seq)
                    print(cirq_parser.extract_context())
                    cirq_parser.sequence_length = self.sequence_length

                # Add the current operation sequence to our unit
                compute_unit.append(op_seq)
                compute_unit.add_context(*cirq_parser.extract_context())

                # Update remaining sequence length
                cirq_parser.sequence_length = (self.sequence_length * 3 - cirq_parser.curr_mem()) // 3

                # Grab the next sequence
                op_seq = next(op_iter, None)

        # Handle lingering sequence(s), yielding whatever remains
        if len(compute_unit) > 0:
            local_ctx = cirq_parser.extract_context()
            compute_unit.add_context(*local_ctx)
            yield compute_unit

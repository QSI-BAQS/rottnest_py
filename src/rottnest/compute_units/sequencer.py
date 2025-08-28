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
            global_context = None
            ):

        # Map layouts to proxies
        # TODO: determine ownership of this vs ids 

        print("Layouts: ", layouts)
        print("", )
        self._layout_proxies = list(map(LayoutProxy, layouts))
        self.priority_shim = []

        # Worst case: Rz operation on a new qubit induces an input, graph state and
        # teleported qubit 
        self.sequence_length = self._layout_proxies[0].mem_bound() // 3
        

        if global_context is None:
            global_context = QubitLabelTracker()

    def priority(self, gate, layout):
        pass

    def sequence_pyliqtr(self, parser):

        layouts = cycle(self._layout_proxies)
 
        layout = next(layouts) 
        compute_unit = ComputeUnit(layout.layout_id, mem_bound=layout.mem_bound())

        cirq_parser = CirqParser(self.sequence_length)

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

                        layout = next(layouts)
                        # Create a new compute unit
                        compute_unit = ComputeUnit(
                            layout.layout_id,
                            mem_bound=layout.mem_bound()
                        )

                        # Reset the context of the parser
                        cirq_parser.reset_context(op_seq)
                        cirq_parser.sequence_length = self.sequence_length 
                        continue

                curr_memory = cirq_parser.curr_mem()
                # This doesn't track additional qubit allocations

                # Caution that the next sequence doesn't 
                # push us over
                # this should be replaced with a lookahead 
                # rather than a bound
                if ((cirq_parser.sequence_length == 0) 
                    or (cirq_parser.curr_mem() + 3 * op_seq.n_rz_operations + len(op_seq) > 0.8 * compute_unit.memory_bound - MIN_SEQUENCE_LEN)):

                    local_context = cirq_parser.extract_context()
                    compute_unit.add_context(*local_context)
                   
                    #assert False

                    if len(compute_unit) > 0:
                        yield compute_unit

                    # Grab next layout
                    # Eventually replace this with another scheduler
                    # TODO: Investigate composer hooks
                    layout = next(layouts)

                    # Create a new compute unit
                    compute_unit = ComputeUnit(
                        layout.layout_id,
                        mem_bound=layout.mem_bound()
                    )

                    # Reset the context of the parser
                    cirq_parser.reset_context(op_seq)
                    cirq_parser.sequence_length = self.sequence_length
                    continue

                # Add the  sequence
                compute_unit.append(op_seq)

               
                # Reduce sequence length 
                # Worst case is the creation of a new teleported gate 
                cirq_parser.sequence_length = (self.sequence_length * 3 - cirq_parser.curr_mem()) // 3 

        if len(compute_unit) > 0:
            local_context = cirq_parser.extract_context()
            compute_unit.add_context(*local_context)
            if local_context[0] > 0:
                yield compute_unit

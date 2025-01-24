# TODO: Parameterisation
'''
    pyLIQTR gates trigger the call-graph tracker
    Each pyLIQTR gate is decomposed into the following
     - Clifford Shim layer : This will either be a 
        compiled widget, or a set of local operations 
     - Abstracted compilation sequence : Wrapper for
        the compiled gate   
    If the gate contains no pyLIQTR gates then it is 
    handed off to the widgetiser 
    Otherwise, each child pyLIQTR gate is independently
    compiled 
'''

from pyLIQTR.utils.circuit_decomposition import circuit_decompose_multi

import networkx as nx
import pyLIQTR
import qualtran
import qualtran.bloqs
import qualtran.bloqs.mcmt
import cirq

from pyLIQTR.qubitization import qsvt, qubitized_gates
from pyLIQTR.BlockEncodings.PauliStringLCU import PauliStringLCU 
from pyLIQTR.circuits.operators.select_prepare_pauli import prepare_pauli_lcu
from pyLIQTR.circuits.operators.prepare_oracle_pauli_lcu import QSP_Prepare

from . import cirq_parser

# pyLIQTR gates include cirq gates
known_gates = dict(cirq_parser.known_gates) 

from rottnest.input_parsers.interrupt import INTERRUPT 

# Difficult to assert uniqueness of hash function
def cmp_qsvt(self, other):
   return (self._phis == other._phis
        and self._ ) 

'''
All pyLIQTR gates should be decomposed into their call graph

Each gate is then bound as a shim and a re-usable component 
'''

class PyliqtrCache:

    def __init__(self):
        self._cache = []

    def get(self, gate):
        self._cache.append(gate)

    def append(self, obj):
        self._cache.append(obj)

class PyliqtrGateCache:

    def __init__(self, gate_type, cache_len):
        self.gate_type = gate_type
        self.cache_len = cache_len

class PyliqtrParser:
    tracking_targets = frozenset((
        qsvt.QSVT_real_polynomial,
        PauliStringLCU,
        prepare_pauli_lcu,
        QSP_Prepare,
        qubitized_gates.QubitizedRotation,
        qubitized_gates.QubitizedReflection,
        qualtran.bloqs.mcmt.multi_control_multi_target_pauli.MultiControlPauli,
        qualtran.cirq_interop._bloq_to_cirq.BloqAsCirqGate, # Catch a bunch of qualtran gates
        qualtran.bloqs.mcmt.and_bloq.And,
    ))

    # Targets to decompose on the spot 
    cirq_decomposing_targets = frozenset((
        cirq.ControlledGate,
    ))

    '''
        Begin by collecting the pyliqtr components
    '''
    def __init__(self, circuit=None, op=None, gate=None, sequence_length=1000, handle_id="0"):

        self.handle_id = handle_id

        self.op = op
        self.sequence_length = sequence_length
        self.gate = gate
        
        self.circuit = circuit_decompose_multi(circuit, 1)

        self.shims = {} # Shims represent non-pyliqtr sequences
        self.handles = {} # Handles represent callable representations of pyliqtr objects
        
        self.decompositions = {}
        self.fully_decomposed = None
        self._cache = PyliqtrCache() 

    def qualtran_handoff(self):
        '''
            Hands off to qualtran for the next parsing pass
        '''
        # Requires that the gate has been fully decomposed by pyliqtr
        if self.fully_decomposed: 
            qualtran_parser = QualtranParser(self.circuit) 
            qualtran_parser.parse()
            qualtran_parser.decompose()

    def __call__(self, *args, **kwargs):
        # TODO
        # Should invoke an iterator over decomposition objects
        pass

    def __iter__(self):
        if self.circuit is not None:
            return self.circuit.__iter__()
        raise Exception("Circuit has not been passed")

    def decompose(self, *targs):
        handle_id = 0
        if len(targs) == 0:
            targs = self.handles
        
        for label in targs:
            for gate in self.handles[label]:
                tmp = cirq.Circuit()
                tmp.append(gate)
                parser = PyliqtrParser(tmp, op=gate, handle_id = f"{self.handle_id}_{handle_id}")
                yield parser
                handle_id += 1

    def graph(self):
        if self.op is not None:
            graph, nodes = self.op.gate.call_graph()
            return graph, nodes
        return None, None

    def draw_graph(self):
        graph, gates = self.graph()
        nx.draw_kamada_kawai(graph, labels={i:str(i) for i in gates})
                
    def parse(self, circuit=None):
        # This is the decomposition

        self.fully_decomposed = True

        self._curr_shim = cirq_parser.CirqShim() 

        if circuit is None:
            circuit = self.circuit
        for moment in circuit:
            for operation in moment:
                if operation.gate.__class__ in self.tracking_targets:
                    instances = self.handles.get(operation.gate.__class__, list())
                    instances.append(operation) 
                    self.handles[operation.gate.__class__] = instances

                    # Create a new shim object
                    self.shims[operation] = self._curr_shim
                    self._curr_shim = cirq_parser.CirqShim() 
                    
                    # If this is created then 
                    self.fully_decomposed = False
                elif operation.gate.__class__ in self.cirq_decomposing_targets:
                    # TODO: decompose and append to shim 
                    pass
                else:
                    self._curr_shim.append(operation)      


    def unroll_graph(self):
        '''
        Return each circuit object
        '''
        for r in self.decompose():
            # Retrieve shim 
            shim = self.shims[r.op]

            if len(shim) > 0:
                shim_id = f"{r.handle_id}s" 
                yield GraphWrapper(shim_id, f"Shim: {str(r.op.gate)}", None)
            yield GraphWrapper(r.handle_id, str(r.op.gate), parser=r)

    def traverse(self):
        '''
        Return each circuit object
        '''
        for r in self.decompose():
            r.parse()

            # Inject shim
            shim = self.shims[r.op]
            if len(shim) > 0:
                # print("SHIM")
                yield shim 
                yield INTERRUPT()

            if r.fully_decomposed:
                self._cache.append(r)
                yield r
                yield INTERRUPT()

            else:
                # print("UNROLL")
                it = r.traverse()
                while True:
                    try:
                        v = next(it)
                        yield v
                    except StopIteration:
                        break

    def traverse_all(self):
        '''
        Dump the whole circuit 
        '''
        parser = CirqParser(self.sequence_length)
        for circuit in self.traverse(): 
            for ops in parser.parse(circuit): 
                yield ops


class GraphWrapper():
    '''
        Thin graph node wrapper object
    '''
    def __init__(self, handle_id, name, description="", children = None, parser=None):
        self.handle_id = handle_id
        self.name = name
        self.description = description
        self.children = children
        self.parser = parser 

    def get_graph(self): 
        return self.parser

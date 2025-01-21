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

from . import cirq_parser

# pyLIQTR gates include cirq gates
known_gates = dict(cirq_parser.known_gates) 


#known_gates |= {
#    pyLIQTR.qubitization.qsvt.QSVT_real_polynomial
#}

# Difficult to assert uniqueness of hash function
def cmp_qsvt(self, other):
   return (self._phis == other._phis
        and self._ ) 

'''
All pyLIQTR gates should be decomposed into their call graph

Each gate is then bound as a shim and a re-usable component 
'''


class PyliqtrParser:
    tracking_targets = frozenset((
        qsvt.QSVT_real_polynomial,
        qubitized_gates.QubitizedRotation,
        qubitized_gates.QubitizedReflection,
        qualtran.bloqs.mcmt.multi_control_multi_target_pauli.MultiControlPauli,
        qualtran.cirq_interop._bloq_to_cirq.BloqAsCirqGate, # Catch a bunch of qualtran gates
        qualtran.bloqs.mcmt.and_bloq.And,
    ))

    '''
        Begin by collecting the pyliqtr components
    '''
    def __init__(self, circuit=None, op=None, gate=None, sequence_length=1000):
        self.op = op
        self.sequence_length = sequence_length
        self.gate = gate
        
        self.circuit = circuit_decompose_multi(circuit, 1)
        self._curr_shim = []
        self.shims = {} # Shims represent non-pyliqtr sequences
        self.handles = {} # Handles represent callable representations of pyliqtr objects
        
        self.decompositions = {}
        self.fully_decomposed = None

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
        if len(targs) == 0:
            targs = self.handles
        
        for label in targs:
            for gate in self.handles[label]:
                tmp = cirq.Circuit()
                tmp.append(gate)
                parser = PyliqtrParser(tmp, op=gate)
                yield parser

    def graph(self):
        if self.op is not None:
            graph, nodes = self.op.gate.call_graph()
            return graph, nodes
        return None, None

    def draw_graph(self):
        graph, gates = self.graph()
        nx.draw_kamada_kawai(graph, labels={i:str(i) for i in gates})
                
    def parse(self, circuit=None):
        self.fully_decomposed = True
        if circuit is None:
            circuit = self.circuit
        for moment in circuit:
            for operation in moment:
                if operation.gate.__class__ in self.tracking_targets:
                    instances = self.handles.get(operation.gate.__class__, list())
                    instances.append(operation) 
                    self.handles[operation.gate.__class__] = instances
                    self.shims[operation] = self._curr_shim
                    self._curr_shim = []
                    self.fully_decomposed = False
                else:
                    self._curr_shim.append(operation)      

    def traverse(self):
        '''
        Return each circuit object
        '''
        for r in self.decompose():
            r.parse()
            if r.fully_decomposed:
                yield r
            else:
                it = r.traverse()
                while True:
                    try:
                        v = next(it)
                        yield v
                    except:
                        break

    def traverse_all(self):
        '''
        Dump the whole circuit 
        '''
        parser = CirqParser(self.sequence_length)
        for circuit in self.traverse(): 
            for ops in parser.parse(circuit): 
                yield ops

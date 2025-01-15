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
import networkx as nx
import pyLIQTR
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



class CliffordShim:
    '''
        Shim layer of cliffords 
        May act as its own widget, or may simply be injected on the idle data qubits     
    '''
    def __init__(self, gates):
        pass 

  
    def append(self, gate):  
        pass


class CallGraph:
    '''
        Call Graph object associated with a PyLiqtr gate
    '''
    
    def __init__(self, operation): 
        self._graph, self._gates = operation.gate.call_graph() 
        # Find the roots, then perform the layering
        self._roots = [
            i for i in self._graph
            if not any(graph.predecessors(i))
        ] 

        self._layers = nx.bfs_layers(
            self._graph,
            self._roots
        )  

    def compile(self):
        pass


class PyliqtrParser:
    tracking_targets = frozenset((
        qsvt.QSVT_real_polynomial,
        qubitized_gates.QubitizedRotation,
        qubitized_gates.QubitizedReflection,
    ))

    '''
        Begin by collecting the pyliqtr components
    '''
    def __init__(self):
        self._curr_shim = []
        self.shims = {} # Shims represent non-pyliqtr sequences
        self.handles = {} # Handles represent callable representations of pyliqtr objects
        
        self.decompositions = {}

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)

    def decompose(self, *targs):
        if len(targs) == 0:
            targs = self.handles
        
        for label in targs:
            for gate in self.handles[label]:
                tmp = cirq.Circuit()
                tmp.append(gate)

                decomp = circuit_decompose_multi(tmp, 1)

                parser = PyliqtrParser()
                parser(decomp)
                yield parser
                
    def parse(self, circuit):
        '''
        TODO: Shim Logic
        '''
        for moment in circuit:
            for operation in moment:
                if operation.gate.__class__ in self.tracking_targets:
                    instances = self.handles.get(operation.gate.__class__, list())
                    instances.append(operation) 
                    self.handles[gate.__class__] = instances
                    self.shims[operation] = self._curr_shim
                    self._curr_shim = []
                else:
                    self._curr_shim.append(operation)

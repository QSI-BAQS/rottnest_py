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

from . import cirq_parser

# pyLIQTR gates include cirq gates
known_gates = dict(cirq_parser.known_gates) 


known_gates |= {
    pyLIQTR.qubitization.qsvt.QSVT_real_polynomial: 'LIQ'
}

'''
All pyLIQTR gates should be decomposed into their call graph

Each gate is then bound as a shim and a re-usable component 
'''


class CliffordShim:
    '''
        Shim layer of cliffords 
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

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
from cirq.ops.raw_types import _InverseCompositeGate

from rottnest.pandora.pandora_sequencer import PandoraSequencer 

from . import cirq_parser
from rottnest.monkey_patchers import pyliqtr_patcher, qualtran_patcher
from rottnest.pandora.pandora_cache import pandora_cache

# pyLIQTR gates include cirq gates
known_gates = dict(cirq_parser.known_gates) 

# Used to cache results 
local_cache = set() 
local_cache_tag = None

# Todo: move this to a pandora module

from rottnest.input_parsers.interrupt import INTERRUPT, CACHED, NON_CACHING

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
        PauliStringLCU,
        prepare_pauli_lcu,
        QSP_Prepare,
        qubitized_gates.QubitizedRotation,
        qubitized_gates.QubitizedReflection,
        qualtran.bloqs.mcmt.multi_control_multi_target_pauli.MultiControlPauli,
        qualtran.cirq_interop._bloq_to_cirq.BloqAsCirqGate, # Catch a bunch of qualtran gates
        qualtran._infra.adjoint.Adjoint,
        qualtran.bloqs.multiplexers.select_pauli_lcu.SelectPauliLCU,
    _InverseCompositeGate,
    ))

    # Targets to decompose on the spot 
    cirq_decomposing_targets = frozenset((
        cirq.ControlledGate,
        qualtran.bloqs.mcmt.and_bloq.And,
    ))

    '''
        Begin by collecting the pyliqtr components
    '''
    def __init__(self, circuit=None, op=None, gate=None, sequence_length=1000, cache=True):

        self.op = op
        self.sequence_length = sequence_length
        self.gate = gate
        
        self.circuit = circuit_decompose_multi(circuit, 1)
        self.n_qubits = len(self.circuit.all_qubits()) 

        self.shims = [] # Shims represent non-pyliqtr sequences
        self.handles = {} # Handles represent callable representations of pyliqtr objects
        self.sequence = []
        
        self.decompositions = {}
        self.fully_decomposed = None
        self._caching = True
        self.rottnest_hash = None

    def __call__(self, *args, **kwargs):
        # TODO
        # Should invoke an iterator over decomposition objects
        pass

    def __iter__(self):
        if self.circuit is not None:
            return self.circuit.__iter__()
        raise Exception("Circuit has not been passed")

    def decompose(self, *targs):
        '''
            TODO: docstring
        '''
        # Sequence is a valid ordering of the operations 
        for shim, gate in zip(self.shims, self.sequence):

            # Yield shim
            if len(shim) > 0: 
                yield shim

            if gate is None:
                continue

            # Cache check
            rottnest_hash = gate._rottnest_hash()
            if rottnest_hash is not None and self._caching:
                if rottnest_hash in local_cache:  
                    non_participatory = len(
                        self.circuit.all_qubits().difference(gate._qubits)
                    )
                    yield CACHED(rottnest_hash, request_type=CACHED.REQUEST, non_participatory_qubits=non_participatory)
                    continue
                else:
                    local_cache.add(rottnest_hash)

            # Wrap the gate as a cirq cirquit
            tmp = cirq.Circuit()
            tmp.append(gate)

            parser = PyliqtrParser(tmp, op=gate, cache=self._caching)
            if rottnest_hash is not None:
                parser.rottnest_hash = rottnest_hash
                non_participatory = len(
                    self.circuit.all_qubits().difference(tmp.all_qubits())
                )
                yield CACHED(rottnest_hash, request_type=CACHED.START, non_participatory_qubits=non_participatory)
                op = parser.op
                if op is not None:
                    op = type(op.gate).__name__
                pandora_seq = pandora_cache.in_cache(op, hash_obj = parser.rottnest_hash)
                if pandora_seq is not None:
                    yield pandora_seq
                else:
                    yield parser
                yield CACHED(rottnest_hash, request_type=CACHED.END)
            else:
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
        # This is the decomposition
        self.fully_decomposed = True

        _curr_shim = cirq_parser.CirqShim() 

        if circuit is None:
            circuit = self.circuit

        for moment in circuit:
            for operation in moment:

                if operation.gate.__class__ in self.tracking_targets:
                    # Tracking object
                    # Add to sequence, create new shim

                    self.sequence.append(operation)

                    if operation._rottnest_hash() is None:
                        raise Exception("All Tracking targets should implement a hash")

                    _curr_shim.set_parent(operation)
                    self.shims.append(_curr_shim)
                    _curr_shim = cirq_parser.CirqShim() 
            
                    # If this is created then 
                    self.fully_decomposed = False

                elif operation.gate.__class__ in self.cirq_decomposing_targets:
                    # TODO: Flatten this into a regular decomposition
                    # Force cirq decomposition to shim
                    # For now just hope that these aren't nested
                    for g in cirq.decompose(operation):
                        if g.gate.__class__ in self.tracking_targets:
                            self.sequence.append(g)

                            _curr_shim.set_parent(operation)
                            self.shims.append(_curr_shim)
                            _curr_shim = cirq_parser.CirqShim() 
                                                    
                            self.fully_decomposed = False
                        else:
                            _curr_shim.append(g)

                else:
                    # Operation is directly added to the shim
                    _curr_shim.append(operation)      
        # Terminating shim for any remaining operations
        self.shims.append(_curr_shim)
        
        # Terminal none on the sequence
        self.sequence.append(None)


    def unroll_graph(self, prefix=''):
        '''
        Return each circuit object
        '''
        if prefix != '':
            prefix += '_'

        handle_idx = 0

        for r in self.decompose():
            r.parse()
            # TODO: re-wrangle this
            if r == INTERRUPT:
                if (r.cache_hash() is NON_CACHING 
                    or r.request_type is CACHED.START 
                    or r.request_type is CACHED.END): 
                        continue

                yield GraphWrapper(
                    f"{prefix}{handle_idx}c",
                    name=None,
                    rottnest_hash = r.cache_hash()
                ) 
                handle_idx += 1
                continue

            if isinstance(r, cirq_parser.CirqShim):
                shim_id = f"{prefix}{handle_idx}s" 
                yield GraphWrapper(shim_id, str(r), parser=r)
                continue

            if isinstance(r, PandoraSequencer):
                shim_id = f"{prefix}{handle_idx}p" 
                yield GraphWrapper(shim_id, str(r), parser=r)
                continue

            yield GraphWrapper(f"{prefix}{handle_idx}", str(getattr(getattr(r, "op", None), "gate", "Missing attr")), parser=r, rottnest_hash=r.rottnest_hash)
            handle_idx += 1

    def traverse(self):
        '''
            Return each circuit object
        '''
        for r in self.decompose():
            r.parse()

            if r.fully_decomposed:
                yield r
                yield INTERRUPT

            else:
                it = r.traverse()
                while True:
                    try:
                        v = next(it)
                        yield v
                    except StopIteration:
                        break
                yield INTERRUPT

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
    def __init__(self, handle_id, name, description="", parser=None, rottnest_hash=None):
        self.handle_id = handle_id
        self.rottnest_hash = rottnest_hash 

        self.name = name
        self.description = description
        self.parser = parser 

    def get_graph(self): 
        return self.parser

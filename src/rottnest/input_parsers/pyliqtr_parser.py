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

from types import MethodType, NoneType

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

from cirq import DecompositionContext, SimpleQubitManager

from qualtran.cirq_interop._bloq_to_cirq import BloqAsCirqGate

#from rottnest.pandora.pandora_sequencer import PandoraSequencer

from . import cirq_parser
from . import graph_wrapper

from .graph_wrapper import GraphWrapper

from rottnest.monkey_patchers import add_pyliqtr_hash
from rottnest.pandora.pandora_cache import pandora_cache

# pyLIQTR gates include cirq gates
known_gates = dict(cirq_parser.known_gates)


# Todo: move this to a pandora module

from rottnest.input_parsers.interrupt import INTERRUPT, CACHED, NON_CACHING

# TODO ???
# Difficult to assert uniqueness of hash function
def cmp_qsvt(self, other):
   return (self._phis == other._phis
        and self._ )

'''
All pyLIQTR gates should be decomposed into their call graph

Each gate is then bound as a shim and a re-usable component
'''
class PyliqtrParser:
    tracking_targets = set()

    # Used to cache results
    # This is a singleton
    local_cache = set()
    local_cache_tag = None

    @classmethod
    def set_cache_tag(cls, layout_ids):
        '''
            Sets the current cache tag
            This should reset on layout update
            This is a class method as the cache can be shared by all parsers
        '''
        if cls.local_cache_tag != layout_ids:
            cls.local_cache_tag = layout_ids
            cls.local_cache = set()

    @classmethod
    def force_cache_flush(cls):
        # Reset to base (under no circumstance should None ever
        # be given to set_cache_tag)
        cls.local_cache_tag = None
        cls.local_cache = set()

    # Targets to decompose on the spot
    cirq_decomposing_targets = frozenset((
        cirq.ControlledGate,
        qualtran.bloqs.mcmt.and_bloq.And,
        cirq.CCXPowGate,
    ))

    @classmethod
    def update_tracking_targets(cls, targets):
        '''
            Injects new tracking targets
        '''
        cls.tracking_targets |= targets

    '''
        Begin by collecting the pyliqtr components
    '''
    def __init__(self, circuit=None, op=None, gate=None, sequence_length=1000, decomp_context=None, cache=True):

        self.op = op
        self.sequence_length = sequence_length
        self.gate = gate

        if decomp_context is None:
            decomp_context = DecompositionContext(qubit_manager=SimpleQubitManager())
        self._context = decomp_context

        self.circuit = circuit_decompose_multi(circuit, 1, context=self._context)
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
                if rottnest_hash in self.local_cache:
                    non_participatory = len(
                        self.circuit.all_qubits().difference(gate._qubits)
                    )
                    # Need a mapping here
                    yield CACHED(
                        rottnest_hash,
                        request_type=CACHED.REQUEST,
                        op=gate,
                        non_participatory_qubits=non_participatory
                    )
                    continue
                else:
                    self.local_cache.add(rottnest_hash)

            # Wrap the gate as a cirq cirquit
            tmp = cirq.Circuit()
            tmp.append(gate)

            parser = PyliqtrParser(tmp, op=gate, cache=self._caching, decomp_context=self._context)
            if rottnest_hash is not None:
                parser.rottnest_hash = rottnest_hash

                non_participatory = (
                    self.circuit.all_qubits().difference(tmp.all_qubits())
                )

                participatory = (
                    tmp.all_qubits()
                )

                yield CACHED(
                    rottnest_hash,
                    request_type=CACHED.START,
                    op=gate,
                    non_participatory_qubits=len(non_participatory)
                )

                op = parser.op
                pandora_seq = pandora_cache.in_cache(op, spawn=True)

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
                tracking_identity = operation.gate.__class__

                if tracking_identity in [ BloqAsCirqGate ]:
                    tracking_identity = type(operation.gate.bloq)

                if tracking_identity in self.tracking_targets:
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

                elif tracking_identity in self.cirq_decomposing_targets:
                    # TODO: Flatten this into a regular decomposition
                    # Force cirq decomposition to shim
                    # For now just hope that these aren't nested
                    self.fully_decomposed = False

                    for g in cirq.decompose(operation):
                        g_identity = g.gate.__class__

                        # TODO : Wrappers should be a class-level frozenset
                        if g_identity in [ BloqAsCirqGate ]:
                            g_identity = type(g.gate.bloq)

                        # In case the gate decomposes into tracking targets
                        if g_identity in self.tracking_targets:
                            self.sequence.append(g)

                            _curr_shim.set_parent(operation)
                            self.shims.append(_curr_shim)
                            _curr_shim = cirq_parser.CirqShim()

                        else:
                            # Native gate
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

            # TODO: Fix import cycle on pandora sequencer
            if isinstance(r, type(None)): #PandoraSequencer):
                # Set the pandora union find based on the architecture
                pandora_cache.architecture_bind(r, arch_ids[0])

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


def rottnest_cacheable(cls, hash_fn=None):
    '''
        Registers a class as cacheable

        IN:
            cls [Class]
                The class to register

            hash_fn [None | Callable]
                The function to register as its hash function
                If None, assumes that _rottnest_hash (internal binding) is its hash function
                If not None, ensures that either;
                    1. The function IS cls._rottnest_hash
                        or
                    2. The class does not implement a _rottnest_hash
                If the function passed in is not _rottnest_hash, exposes that function
                as the class' _rottnest_hash

        OUT: [Class]
            Returns the input cls, acting as the identify function for the class object
            This ensures the function can be used as a class decorator

            NOTE: As a decorator, will not mutate the input class
            NOTE: As a decorator, cannot be given a hash_fn argument - hence, any
                  decorated class MUST implement _rottnest_hash

        EFFECTS:
            Registers the class with the pyliqtr_patcher and the PyliqtrParser
            as one that should be cached when encountered

            Can be safely repeated on a class
    '''
    if hash_fn is None:
        hash_fn = cls._rottnest_hash
    else:
        if hasattr(cls, "_rottnest_hash") and hash_fn is not cls._rottnest_hash:
            raise TypeError(f"Class {cls} implements _rottnest_hash, but a different function was passed as its hashing function.\nEither implement its hash function as _rottnest_hash, or do not define your own separate _rottnest_hash")
        cls._rottnest_hash = MethodType(hash_fn)

    assert False
    add_pyliqtr_hash(cls, hash_fn)
    PyliqtrParser.update_tracking_targets({cls})

    return cls

def update_tracking_targets(targets):
    '''
        Singleton dispatch
    '''
    PyliqtrParser.update_tracking_targets(targets)

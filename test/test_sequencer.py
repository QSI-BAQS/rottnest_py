import unittest

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED, NON_CACHING
from rottnest.input_parsers.cirq_parser import CirqParser, shared_rz_tag_tracker
from rottnest.compute_units.sequencer import Sequencer
from rottnest.widget_compilers.compiler_flow import run_widget

from rottnest.pandora.pandora_sequencer import PandoraSequencer


import pyLIQTR
import qualtran

# imports
import numpy as np
import time
import cirq
import qualtran as qt
import requests
import json
import pandas as pd
#from rigetti_resource_estimation import gs_equivalence as gseq
#from rigetti_resource_estimation.estimation_pipeline import estimation_pipeline
#from rigetti_resource_estimation import widgetization00
#from rigetti_resource_estimation import transpile
#from rigetti_resource_estimation import translators

# pyLIQTR 1.3.3
from pyLIQTR.ProblemInstances.getInstance import getInstance
from pyLIQTR.clam.lattice_definitions import SquareLattice, TriangularLattice
from pyLIQTR.BlockEncodings.getEncoding import getEncoding, VALID_ENCODINGS
from pyLIQTR.qubitization.qsvt_dynamics import qsvt_dynamics, simulation_phases
from pyLIQTR.qubitization.qubitized_gates import QubitizedWalkOperator
from pyLIQTR.circuits.operators.AddMod import AddMod as pyLAM

# https://github.com/isi-usc-edu/qb-gsee-benchmark, commit 4c547e8
from qb_gsee_benchmark.qre import get_df_qpe_circuit
from qb_gsee_benchmark.utils import retrieve_fcidump_from_sftp

# pyscf v2.7.0
from pyscf  import ao2mo, tools

# openfermion v1.6.1
from openfermion import InteractionOperator

from pyLIQTR.utils.circuit_decomposition import circuit_decompose_multi


from rottnest.compute_units.architecture_proxy import ArchitectureProxy, saved_architectures
def arch_constructor(n_qubits):
    class ProxyArch(ArchitectureProxy):
        def __new__(cls):
            return object.__new__(ProxyArch)

        def check_pregenerated(self):
            return True

        def __init__(self, *args, **kwargs):
            pass

        def num_qubits(self):
            return n_qubits

        def mem_bound(self):
            return n_qubits

        def underlying_json(self):
            return ""

    saved_architectures[666] = object()
    saved_architectures[666] = ProxyArch()
    return 666

def make_qsvt_circuit(model,encoding,times=1.0,p_algo=0.95):
    """Make a QSVT based circuit from pyLIQTR"""
    eps = (1 - p_algo) / 2
    scaled_times = times * model.alpha
    phases = simulation_phases(times=scaled_times, eps=eps, precompute=False, phase_algorithm="random")
    gate_qsvt = qsvt_dynamics(encoding=encoding, instance=model, phase_sets=phases)
    return gate_qsvt.circuit

def make_fh_circuit(N=2, times=1.0, p_algo=0.95):
    """Helper function to build Fermi-Hubbard circuit."""
    # Create Fermi-Hubbard Instance
    J = -1.0
    U = 2.0
    model = getInstance("FermiHubbard", shape=(N, N), J=J, U=U, cell=SquareLattice)
    return make_qsvt_circuit(model,encoding=getEncoding(VALID_ENCODINGS.PauliLCU),times=times,p_algo=p_algo)


def cirq_len(op):
    lengths = { cirq.Rx: 3, cirq.Ry: 5, }

    singles = {
        cirq.ops.common_gates.HPowGate,
        cirq.ops.common_gates.XPowGate,
        cirq.ops.common_gates.YPowGate,
        cirq.ops.common_gates.ZPowGate,
        cirq.Rz,
        cirq.ops.pauli_gates._PauliX,
        cirq.ops.pauli_gates._PauliY,
        cirq.ops.pauli_gates._PauliZ,
        cirq.ops.common_gates.CXPowGate,
        cirq.ops.common_gates.CZPowGate,
        cirq.T,
        cirq.ops.common_gates.MeasurementGate,
    }

    if op.gate.__class__ in lengths:
        return lengths[op.gate.__class__]
    else:
        return int(op in singles)

def reference_decomp(circuit, depth=None):
    for v in pyLIQTR.utils.circuit_decomposition.circuit_decompose_multi(circuit, depth):
        for operation in v:
            yield operation

# Mock cache interface to allow composing over cache requests
class CircuitCache:
    def __init__(self):
        self.cache = {}
        self.cache_stack = []
        self.curr_entry = None
        self.curr_hash = None

    def start(self, cache_obj):
        self.curr_hash = cache_obj.cache_hash()
        if self.curr_entry is not None:
            self.cache_stack.append(self.curr_entry)

        self.curr_entry = CacheEntry(self.curr_hash)

    def insert(self, v):
        if self.curr_entry is not None:
            self.curr_entry.insert(v)

    def end(self, cache_obj):
        if self.curr_entry is None:
            raise Exception("Ended empty cache")

        hsh = cache_obj.cache_hash()
        if hsh != self.curr_hash:
            raise Exception("Cache mismatch")

        closed_entry = self.curr_entry
        self.cache[hsh] = closed_entry

        if self.cache_stack:
            self.curr_entry = self.cache_stack.pop()
            self.curr_entry.add_child(closed_entry)
            self.curr_hash = self.curr_entry.hsh
        else:
            self.curr_entry = None
            self.curr_hash = None

    def request(self, cache_obj):
        hsh = cache_obj.cache_hash()
        if hsh not in self.cache:
            raise Exception("Cache miss")

        self.curr_entry.add_child(self.cache[hsh])

        return self.cache[hsh].request()


class CacheEntry:
    def __init__(self, hsh):
        self.hsh = hsh
        self.sequence = []

    def insert(self, v):
        self.sequence.append(v)

    def add_child(self, child):
        self.sequence.append(child)

    def request(self):
        for v in self.sequence:
            if isinstance(v, CacheEntry):
                yield from v.request()
            else:
                yield v


def decomp_to_partial_seq(decomp):
    partial_sequence = {}

    for v in decomp:
        for qb in v.qubits:
            qb_ordering = partial_sequence.get(qb, None)
            if qb_ordering is None:
                partial_sequence[qb] = [v.gate.__class__]
            else:
                qb_ordering.append(v.gate.__class__)

    return partial_sequence

def match_partial_seq(seq, qb, gatecls):
    target = seq[qb]
    res = (targ_top := target.pop(0)) == gatecls
    if not res:
        print(targ_top, "expected, got", gatecls, "for qubit", qb)
    if len(target) == 0:
        seq[qb] = None

    return res

def completed_partial_seq(seq):
    return all(val is None for val in seq.values())



class TestSequencer(unittest.TestCase):

    # Covered by the gate count test
    @unittest.SkipTest
    def test_fh(self, N=2, debug=True):
        if debug:
            start = time.time()
            print(f"Creating Fermi Hubbard {N}x{N} from PyLIQTR")
        fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)
        #fh = make_fh_circuit(N=N, p_algo=0.9, times=0.1)

        if debug:
            runtime = time.time() - start
            print(f"\t Completed Generation in {runtime} seconds")

        parser = PyliqtrParser(fh)
        parser.parse()

        arch = arch_constructor(100)
        seq = Sequencer(arch)

        if debug:
            start = time.time()
            print("Parsing PyLIQTR object")

        cnt = 0
        for compute_unit in seq.sequence_pyliqtr(parser):

            if compute_unit != INTERRUPT:
                widget = compute_unit.compile_graph_state()
                #run_widget(cabaliser_obj=widget.json(), region_obj=test_region_obj, full_output=False, rz_tag_tracker=shared_rz_tag_tracker)
                cnt += 1
                print(widget)
                # raise Exception

        if debug:
            runtime = time.time() - start
            print(f"\t Completed Compilation in {runtime} seconds")
            print("Total Widgets: ", cnt)
        #return compute_unit


    @unittest.SkipTest
    def test_fh_validate(self, N=2):
        '''
            Validate the partial sequence our sequence produces vs
            a standard Pyliqtr decomp

            (NOTE: Probably fails due to gate decomp differences?)
        '''
        fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)

        parser = PyliqtrParser(fh)
        parser.parse()

        arch = arch_constructor(100)
        seq = Sequencer(arch)

        decomp = reference_decomp(fh)

        partial_sequence = decomp_to_partial_seq(decomp)

        cache = CircuitCache()

        for t in parser.traverse():
            if t == INTERRUPT:
                if t.cache_hash() is NON_CACHING:
                    pass
                elif t.request_type == CACHED.START:
                    cache.start(t)
                elif t.request_type == CACHED.END:
                    cache.end(t)
                elif t.request_type == CACHED.REQUEST:
                    for operation in cache.request(t):
                        cache.insert(operation)
                        for qb in operation.qubits:
                            self.assertTrue(match_partial_seq(
                                partial_sequence, qb, operation.gate.__class__
                            ))

            else:
                for moment in t:
                    for operation in moment:
                        cache.insert(operation)
                        for qb in operation.qubits:
                            self.assertTrue(match_partial_seq(
                                partial_sequence, qb, operation.gate.__class__
                            ))

        self.assertTrue(completed_partial_seq(partial_sequence))


    def test_fh_gate_count(self, N=2):
        fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)

        parser = PyliqtrParser(fh)
        parser.parse()

        gate_count = 0

        arch = arch_constructor(100)
        seq = Sequencer(arch)

        decomp = reference_decomp(fh)

        ref_gate_count = 0

        for operation in decomp:
            ref_gate_count += cirq_len(operation)

        cache = CircuitCache()

        # Reduce parser to entire circuit
        operations = []
        for t in parser.traverse():
            if t == INTERRUPT:
                if t.cache_hash() is NON_CACHING:
                    pass
                elif t.request_type == CACHED.START:
                    cache.start(t)
                elif t.request_type == CACHED.END:
                    cache.end(t)
                elif t.request_type == CACHED.REQUEST:
                    for operation in cache.request(t):
                        gate_count += cirq_len(operation)
                        cache.insert(operation)
            else:
                if isinstance(t, PandoraSequencer):
                    t = t.to_operation_sequence()
                for moment in t:
                    for operation in moment:
                        gate_count += cirq_len(operation)
                        cache.insert(operation)

        self.assertTrue(ref_gate_count == gate_count)


import sys
if __name__ == '__main__':
    #unittest.main()
    #   n_qubits = 3 
    #   if len(sys.argv) > 1:
    #       n_qubits = int(sys.argv[1])
    st = TestSequencer()
    #   x = st.test_fh(N=n_qubits)
    st.test_fh_gate_count(N=3)
    #   # st.test_fh_validate()
#

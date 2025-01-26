import unittest

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser, shared_rz_tag_tracker
from rottnest.compute_units.sequencer import Sequencer
from rottnest.widget_compilers.compiler_flow import run_widget

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

with open('region_test_obj.json') as f:
    test_region_obj = json.load(f)

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

class SequencerTest(unittest.TestCase):

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
            #]if cnt == 16:
            #]    assert False
            widget = compute_unit.compile_graph_state()
            run_widget(cabaliser_obj=widget.json(), region_obj=test_region_obj, full_output=False, rz_tag_tracker=shared_rz_tag_tracker)
            cnt += 1

        if debug:
            runtime = time.time() - start
            print(f"\t Completed Compilation in {runtime} seconds")
            print("Total Widgets: ", cnt)
        #return compute_unit

import sys
if __name__ == '__main__':
    n_qubits = 10
    if len(sys.argv) > 1:
        n_qubits = int(sys.argv[1])
    st = SequencerTest()
    x = st.test_fh(N=n_qubits)

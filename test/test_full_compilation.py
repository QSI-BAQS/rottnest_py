import numpy as np
import time
import unittest


from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser

from rottnest.input_parsers.interrupt import INTERRUPT
from rottnest.widget_compilers.compiler_flow import run_widget

from pyLIQTR.ProblemInstances.getInstance import getInstance
from pyLIQTR.clam.lattice_definitions import SquareLattice, TriangularLattice
from pyLIQTR.BlockEncodings.getEncoding import getEncoding, VALID_ENCODINGS
from pyLIQTR.qubitization.qsvt_dynamics import qsvt_dynamics, simulation_phases
from pyLIQTR.qubitization.qubitized_gates import QubitizedWalkOperator
from pyLIQTR.circuits.operators.AddMod import AddMod as pyLAM


from rottnest.executables.executables import FermiHubbard 
from ecj.executable import ECJ

import json

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
        
        def mem_bound(self):
            return n_qubits
        
        def underlying_json(self):
            return ""

    saved_architectures[666] = object()
    saved_architectures[666] = ProxyArch() 
    return 666 

class SequencerTest(unittest.TestCase):

    def test_fh(self, N=2, debug=True):

        if debug:
            start = time.time()
            print(f"Creating Fermi Hubbard {N}x{N} from PyLIQTR")
        fh = ECJ(1, 1)()#(N=N,p_algo=0.9999999904,times=0.01)
        #fh = make_fh_circuit(N=N, p_algo=0.9, times=0.1)

        if debug:
            runtime = time.time() - start
            print(f"\t Completed Generation in {runtime} seconds")

        parser = PyliqtrParser(fh)
        parser.parse()


        n_qubits = 50
        arch = arch_constructor(n_qubits) 
        seq = Sequencer(arch)

        if debug:
            start = time.time()
            print("Parsing PyLIQTR object")

        cnt = 0
        for compute_unit in seq.sequence_pyliqtr(parser):

            if compute_unit != INTERRUPT: 
                widget = compute_unit.compile_graph_state()
                run_widget(
                    cabaliser_obj=widget.json(),
                    region_obj=test_region_obj,
                    full_output=False,
                    rz_tag_tracker=shared_rz_tag_tracker
                )
                cnt += 1

        if debug:
            runtime = time.time() - start
            print(f"\t Completed Compilation in {runtime} seconds")
            print("Total Widgets: ", cnt)
        #return compute_unit

import sys
if __name__ == '__main__':
    n_qubits = 5 
    if len(sys.argv) > 1:
        n_qubits = int(sys.argv[1])
    st = SequencerTest()
    x = st.test_fh(N=n_qubits)

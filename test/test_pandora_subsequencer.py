import unittest

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.interrupt import INTERRUPT
from rottnest.input_parsers.cirq_parser import CirqParser, shared_rz_tag_tracker
from rottnest.compute_units.sequencer import Sequencer
from rottnest.executables.fermi_hubbard import make_fh_circuit
from rottnest.widget_compilers.compiler_flow import run_widget

import pyLIQTR
import qualtran

# imports 
import time

from proxy_arch import arch_factory 

from rottnest.pandora.pandora_cache import pandora_cache, architecture_bind
from rottnest.pandora.pandora_sequencer import PandoraSequencer 

class SequencerTest(unittest.TestCase):

    def test_fh(self, N=70, arch_qubits=100, debug=True):

        if debug:
            start = time.time()
            print(f"Creating Fermi Hubbard {N}x{N} from PyLIQTR")
        fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)

        if debug:
            runtime = time.time() - start
            print(f"\t Completed Generation in {runtime} seconds")

        parser = PyliqtrParser(fh)
        parser.parse()

        arch_id = 666
        arch = arch_factory(n_qubits=arch_qubits, arch_id=arch_id)
        architecture_bind(arch)
        
        seq = Sequencer(arch_id)

        if debug:
            start = time.time()
            print("Parsing PyLIQTR object")

        cnt = 0
        for compute_unit in seq.sequence_pyliqtr(parser):

            if compute_unit != INTERRUPT: 
                # Graph State compilation
                widget = compute_unit.compile_graph_state()

                # Full Compilation
                #run_widget(cabaliser_obj=widget.json(), region_obj=test_region_obj, full_output=False, rz_tag_tracker=shared_rz_tag_tracker)
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

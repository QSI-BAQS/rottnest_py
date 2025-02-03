import numpy as np
import time
import json

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser

from rottnest.executables.fermi_hubbard import make_fh_circuit

from rottnest.region_builder.json_to_region import json_to_layout


with open('region_test_obj.json') as f:
    layout_json = json.load(f)
layout = json_to_layout(layout_json)

from rottnest.compute_units.architecture_proxy import ArchitectureProxy, saved_architectures

# Small instance for testing
N = 2
fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)
parser = PyliqtrParser(fh)
parser.parse()



#        arch = arch_constructor(100) 
#        seq = Sequencer(arch)
#
#        if debug:
#            start = time.time()
#            print("Parsing PyLIQTR object")
#
#        cnt = 0
#        for compute_unit in seq.sequence_pyliqtr(parser):
#
#            if compute_unit != INTERRUPT: 
#                widget = compute_unit.compile_graph_state()
#                run_widget(cabaliser_obj=widget.json(), region_obj=test_region_obj, full_output=False, rz_tag_tracker=shared_rz_tag_tracker)
#                cnt += 1
#
#        if debug:
#            runtime = time.time() - start
#            print(f"\t Completed Compilation in {runtime} seconds")
#            print("Total Widgets: ", cnt)
#        #return compute_unit
#
#import sys
#if __name__ == '__main__':
#    n_qubits = 20
#    if len(sys.argv) > 1:
#        n_qubits = int(sys.argv[1])
#    st = SequencerTest()
#    x = st.test_fh(N=n_qubits)

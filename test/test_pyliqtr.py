import numpy as np
import time

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser

import pyLIQTR
# pyLIQTR 1.3.3
from pyLIQTR.ProblemInstances.getInstance import getInstance
from pyLIQTR.clam.lattice_definitions import SquareLattice, TriangularLattice
from pyLIQTR.BlockEncodings.getEncoding import getEncoding, VALID_ENCODINGS
from pyLIQTR.qubitization.qsvt_dynamics import qsvt_dynamics, simulation_phases


# These next two functions were written by Tyler
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


N = 2  
fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)
parser = PyliqtrParser(fh)
parser.parse()

circ_parser = CirqParser(100)

# Create generator object
for circuit in parser.traverse():
    for seq in circ_parser.parse(circuit):
        pass    
        #print(seq)

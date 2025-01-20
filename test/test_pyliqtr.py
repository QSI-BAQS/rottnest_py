from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser


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




fh = make_fh_circuit(N=2,p_algo=0.9999999904,times=0.01)
parser = PyliqtrParser(fh)
parser.parse()

# Create generator object
circ_parser = CirqParser(100, 100, 100)
for circuit in parser.traverse():
    print(circuit)
    circ_parser.parse(circuit)

'''
This file contains functions that were written by Tyler Wilson are released under and apache license by Rigetti under Apache 2.0. 

Elements of this file have been changed by the authors of this project. In keeping with the terms of the Apache 2.0 license we retain the original copyright notice with attribution.

Copyright 2022-2024 Rigetti & Co, LLC

This Computer Software is developed under Agreement HR00112230006 between Rigetti & Co, LLC and
the Defense Advanced Research Projects Agency (DARPA). Use, duplication, or disclosure is subject
to the restrictions as stated in Agreement HR00112230006 between the Government and the Performer.
This Computer Software is provided to the U.S. Government with Unlimited Rights; refer to LICENSE
file for Data Rights Statements. Any opinions, findings, conclusions or recommendations expressed
in this material are those of the author(s) and do not necessarily reflect the views of the DARPA.

Use of this work other than as specifically authorized by the U.S. Government is licensed under
the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing permissions and limitations under
the License.
'''

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.cirq_parser import CirqParser
from rottnest.compute_units.sequencer import Sequencer


# pyLIQTR 1.3.3
from pyLIQTR.ProblemInstances.getInstance import getInstance
from pyLIQTR.clam.lattice_definitions import SquareLattice
from pyLIQTR.BlockEncodings.getEncoding import getEncoding, VALID_ENCODINGS
from pyLIQTR.qubitization.qsvt_dynamics import qsvt_dynamics, simulation_phases


def make_qsvt_circuit(
        model,
        encoding,
        times=1.0,
        p_algo=0.95):
    """
    Make a QSVT based circuit from pyLIQTR
    """
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

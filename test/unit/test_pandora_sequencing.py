'''
    Testcases related to parsing and sequencing a circuit,
    using pandora to cache circuit components
'''

import cirq
import numpy as np
from types import MethodType

import cabaliser.gates as CGates
from cabaliser.operations import OperationType, opcode_map, SingleQubitOperationType, TwoQubitOperationType, RzQubitOperationType, ConditionalOperationType

from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.compute_units.sequencer import Sequencer
from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.pyliqtr_parser import rottnest_cacheable
from rottnest.input_parsers.interrupt import INTERRUPT

from rottnest.preprocessor.architecture import PreprocessorArchitecture

from rottnest.plugins import architectures

from rottnest.pandora import pandora_connection
from rottnest.pandora.pandora_cache import pandora_cache

from rottnest.executables.t_rz_executable import T_RZ_RottnestExecutable


try:
    from utils.quantum_lib_utils import cirq_circuit_to_gate
except ModuleNotFoundError:
    from .utils.quantum_lib_utils import cirq_circuit_to_gate

def op_to_tuple(op):
    if not isinstance(op, OperationType):
        raise Exception(f"Op {op} ({type(op)}) is not a cabaliser operation")

    typed_op = opcode_map[op.opcode](op)

    if isinstance(typed_op, SingleQubitOperationType):
        return (typed_op.opcode, (typed_op.arg,))
    if isinstance(typed_op, (TwoQubitOperationType, ConditionalOperationType)):
        return (typed_op.opcode, (typed_op.ctrl, typed_op.targ))
    if isinstance(typed_op, RzQubitOperationType):
        return (typed_op.opcode, (typed_op.arg,))


class ToffoliExecutable(T_RZ_RottnestExecutable):
    _qb = [cirq.NamedQubit('a'), cirq.NamedQubit('b'), cirq.NamedQubit('c')]

    _single_toffoli = None

    _layered_toffoli = None

    @staticmethod
    def get_name():
        return "LayeredToffoli"

    @staticmethod
    def get_parameters():
        return T_RZ_RottnestExecutable.base_params


    def _generate_circuit(self):
        return self.double_layered_toffoli()


    def get_qubits(self):
        return self._get_qubits_from_list_of_gates()


    def precompute(self):
        pandora_cache.bind_hash(self.instantiate, self.single_toffoli, hsh="single_toffoli")
        pandora_cache.bind_hash(self.instantiate, self.layered_toffoli, hsh="layered_toffoli")
        rottnest_cacheable(self.single_toffoli())
        rottnest_cacheable(self.layered_toffoli())

    def single_toffoli(self):
        if ToffoliExecutable._single_toffoli is None:
            ToffoliExecutable._single_toffoli =  cirq_circuit_to_gate(
                cirq.Circuit(
                    cirq.H(self._qb[0]),
                    cirq.CNOT(self._qb[1], self._qb[0]),
                    cirq.Rz(rads=-np.pi / 4)(self._qb[0]),
                    cirq.CNOT(self._qb[2], self._qb[0]),
                    cirq.Rz(rads=np.pi / 4)(self._qb[0]),
                    cirq.CNOT(self._qb[2], self._qb[0]),
                    cirq.Rz(rads=-np.pi / 4)(self._qb[0]),
                    cirq.CNOT(self._qb[1], self._qb[0]),
                    cirq.Rz(rads=np.pi / 4)(self._qb[0]),
                    cirq.Rz(rads=np.pi / 4)(self._qb[2]),
                    cirq.CNOT(self._qb[1], self._qb[2]),
                    cirq.Rz(rads=np.pi / 4)(self._qb[1]),
                    cirq.Rz(rads=-np.pi / 4)(self._qb[2]),
                    cirq.CNOT(self._qb[1], self._qb[2]),
                    cirq.H(self._qb[0])
                ), 3, lambda s, so: "single_toffoli", "single_toffoli"
            )
        return ToffoliExecutable._single_toffoli

    def layered_toffoli(self):
        # if ToffoliExecutable._layered_toffoli is None:
        if self._layered_toffoli is None:
            # ToffoliExecutable._layered_toffoli = cirq_circuit_to_gate(
            self._layered_toffoli = cirq_circuit_to_gate(
                cirq.Circuit(self.single_toffoli()().on(*self._qb) for i in range(2)),
                3, lambda s, so: "layered_toffoli", "layered_toffoli"
            )
        # return ToffoliExecutable._layered_toffoli
        return self._layered_toffoli

    def instantiate(self, fn):
        return fn()().on(*self._qb)

    # Double layering required to get past initial decompose
    def double_layered_toffoli(self):
        return cirq.Circuit(self.layered_toffoli()().on(*self._qb) for i in range(2))


layout_id = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(layout_id, layout)

def test_standalone_toffoli():
    executable = ToffoliExecutable()

    executable.precompute()

    architecture = PreprocessorArchitecture
    architectures._force_set_current_architecture(PreprocessorArchitecture)

    PyliqtrParser.set_cache_tag([layout_id])

    parser = PyliqtrParser(executable())
    parser.parse()

    seq = Sequencer(layout_id)
    it = seq.sequence_pyliqtr(parser)

    # NOTE : This validates order of gates, but not ctrl/targ assignment
    # or rz tagging
    toffoli_qubit_0 = [
        CGates.H,
        CGates.CNOT, # Targ
        CGates.RZ,
        CGates.CNOT, # Targ
        CGates.RZ,
        CGates.CNOT, # Targ
        CGates.RZ,
        CGates.CNOT, # Targ
        CGates.RZ,
        CGates.H,
    ]

    toffoli_qubit_1 = [
        CGates.CNOT, # Ctrl
        CGates.CNOT, # Ctrl
        CGates.CNOT, # Ctrl
        CGates.RZ,
        CGates.CNOT, # Ctrl
    ]

    toffoli_qubit_2 = [
        CGates.CNOT, # Ctrl
        CGates.CNOT, # Ctrl
        CGates.RZ,
        CGates.CNOT, # Targ
        CGates.RZ,
        CGates.CNOT, # Targ
    ]

    toffoli_sequence = [
        toffoli_qubit_0,
        toffoli_qubit_1,
        toffoli_qubit_2,
    ]

    n_cache_interactions = 0

    for obj in it:
        if obj == INTERRUPT:
            n_cache_interactions += 1
        else:
            # We expect a singular compute unit containing
            # the whole toffoli
            assert obj.n_gates == 15

            # We expect a single sequence with all toffoli gates present
            seq = obj.sequences[0]

            for op in seq:
                opcode, args = op_to_tuple(op)
                for qb in args:
                    assert toffoli_sequence[qb].pop(0) == opcode

    # 3x nested toffoli requests + 1 pair of cache end/start
    assert n_cache_interactions == 5, f"Got {n_cache_interactions} cache interactions, expected 5"


def test_repeat_toffoli():
    '''
        Test repeating the request for a toffoli, to ensure pandora-level cache can be accessed
    '''
    executable = ToffoliExecutable()

    architecture = PreprocessorArchitecture
    architectures._force_set_current_architecture(PreprocessorArchitecture)

    # Force cache reset
    PyliqtrParser.set_cache_tag([])
    PyliqtrParser.set_cache_tag([layout_id])

    parser = PyliqtrParser(executable())
    parser.parse()

    seq = Sequencer(layout_id)
    it = seq.sequence_pyliqtr(parser)

    # Trigger sequencing, just to ensure sequencing works
    for obj in it:
        pass


if __name__ == "__main__":
    pandora_connection.load_pandora_connection()
    test_standalone_toffoli()
    print(f"---- Repeating Toffoli ----")
    test_repeat_toffoli()

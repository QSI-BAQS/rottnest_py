'''
    a pair of executables:
        1. QASMStringExecutable
            takes as a parameter a string literal containing QASM code
        2. QASMFileExecutable
            takes as a parameter a string literal that is a path to a QASM
            source file
'''

from rottnest.executables.t_rz_executable import T_RZ_RottnestExecutable
from rottnest.plugins.parameters import RottnestParameter

from cirq.contrib.qasm_import import circuit_from_qasm

DEFAULT_QASM_TOFFOLI = '''OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];

h q[0];
CX q[1], q[0];
rz(-pi / 4) q[0];
CX q[2], q[0];
rz(pi / 4) q[0];
CX q[2], q[0];
rz(-pi / 4) q[0];
CX q[1], q[0];
rz(pi / 4) q[0];
rz(pi / 4) q[2];
CX q[1], q[2];
rz(pi / 4) q[1];
rz(-pi / 4) q[2];
CX q[1], q[2];
h q[0];
'''

class QASMStringExecutable(T_RZ_RottnestExecutable):
    @staticmethod
    def get_name():
        return "QASM String Circuit"

    @staticmethod
    def _parameters():
        return {
            "src": (RottnestParameter.CodeString, DEFAULT_QASM_TOFFOLI),
        }


    def _generate_circuit(self):
        # TODO : cache circuit
        return circuit_from_qasm(self.src)


class QASMFileExecutable(T_RZ_RottnestExecutable):
    @staticmethod
    def get_name():
        return "QASM File Circuit"

    @staticmethod
    def _parameters():
        return {
            "file": (str, None),
        }

    def _generate_circuit(self):
        # TODO : cache circuit
        #        error handling
        with open(self.file, 'r') as qasm_srcfile:
            circuit = circuit_from_qasm(qasm_srcfile.read())

        return circuit

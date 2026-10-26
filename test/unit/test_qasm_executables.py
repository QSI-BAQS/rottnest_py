import unittest
import math

import tempfile

from rottnest.plugins import executables

import cirq


class QASMExecutableTests(unittest.TestCase):
    def test_qasm_executables_available(self):
        self.assertTrue(executables.set_current_executable("QASM String Circuit"))
        self.assertIsNotNone(executables.get_current_executable())

        self.assertTrue(executables.set_current_executable("QASM File Circuit"))
        self.assertIsNotNone(executables.get_current_executable())

    def test_trivial_qasm_cicuit(self):
        executables.set_current_executable("QASM String Circuit")
        qasm_source = '''
        OPENQASM 2.0;
        qreg q[2];
        CX q[0], q[1];
        '''
        executables.set_executable_params(src=qasm_source)

        exe = executables.get_current_executable()
        circuit = exe()

        self.assertEqual(len(circuit), 1)

        first_op = circuit.moments[0].operations[0]

        self.assertEqual(first_op.gate, cirq.CX)


    def test_qasm_circuits(self):
        circuit_pairs = [
            # TODO : current supported cirq version lacks 3.0, gate declaration support
            (3,
                '''OPENQASM 2.0;
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
                ''',
                lambda qreg: cirq.Circuit(
                    cirq.H(qreg[0]),
                    cirq.CNOT(qreg[1], qreg[0]),
                    cirq.Rz(rads=-math.pi / 4)(qreg[0]),
                    cirq.CNOT(qreg[2], qreg[0]),
                    cirq.Rz(rads=math.pi / 4)(qreg[0]),
                    cirq.CNOT(qreg[2], qreg[0]),
                    cirq.Rz(rads=-math.pi / 4)(qreg[0]),
                    cirq.CNOT(qreg[1], qreg[0]),
                    cirq.Rz(rads=math.pi / 4)(qreg[0]),
                    cirq.Rz(rads=math.pi / 4)(qreg[2]),
                    cirq.CNOT(qreg[1], qreg[2]),
                    cirq.Rz(rads=math.pi / 4)(qreg[1]),
                    cirq.Rz(rads=-math.pi / 4)(qreg[2]),
                    cirq.CNOT(qreg[1], qreg[2]),
                    cirq.H(qreg[0])
                )
            )
        ]

        for n_qb, qasm_src, circuit_builder in circuit_pairs:
            executables.set_current_executable("QASM String Circuit")

            # NOTE : we depend on the prefix 'q_', as that is what is used
            # by cirq's qasm builder lol
            qreg = cirq.NamedQubit.range(0, n_qb, prefix="q_")

            executables.set_executable_params(src=qasm_src)

            exe = executables.get_current_executable()
            circuit = exe()

            self.assertEqual(circuit, circuit_builder(qreg))


        for n_qb, qasm_src, circuit_builder in circuit_pairs:
            # no buffering so write is immediately available
            with tempfile.NamedTemporaryFile(buffering=0) as tmp_f:
                tmp_f.write(qasm_src.encode('utf8'))

                executables.set_current_executable("QASM File Circuit")

                qreg = cirq.NamedQubit.range(0, n_qb, prefix="q_")

                executables.set_executable_params(file=tmp_f.name)

                exe = executables.get_current_executable()
                circuit = exe()

                self.assertEqual(circuit, circuit_builder(qreg))






if __name__ == "__main__":
    unittest.main()

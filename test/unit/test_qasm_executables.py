import unittest
import math

import itertools

import tempfile

from rottnest.plugins import architectures, executables

from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.compute_units.compilation_producers import generate_compute_units

import cirq

# global sets of qasm -> cirq pairs to validate
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


class QASMExecutableTests(unittest.TestCase):
    def test_qasm_executables_available(self):
        executables.set_current_option("QASM String Circuit")
        self.assertIsNotNone(executables.get_current_option())

        executables.set_current_option("QASM File Circuit")
        self.assertIsNotNone(executables.get_current_option())

    def test_trivial_qasm_circuit(self):
        executables.set_current_option("QASM String Circuit")
        qasm_source = '''
        OPENQASM 2.0;
        qreg q[2];
        CX q[0], q[1];
        '''
        executables.set_params_from_kwargs(src=qasm_source)

        exe = executables.get_current_option()
        circuit = exe()

        self.assertEqual(len(circuit), 1)

        first_op = circuit.moments[0].operations[0]

        self.assertEqual(first_op.gate, cirq.CX)


    def test_qasm_circuits(self):
        for n_qb, qasm_src, circuit_builder in circuit_pairs:
            executables.set_current_option("QASM String Circuit")

            # NOTE : we depend on the prefix 'q_', as that is what is used
            # by cirq's qasm builder lol
            qreg = cirq.NamedQubit.range(0, n_qb, prefix="q_")

            executables.set_params_from_kwargs(src=qasm_src)

            exe = executables.get_current_option()
            circuit = exe()

            self.assertEqual(circuit, circuit_builder(qreg))


        for n_qb, qasm_src, circuit_builder in circuit_pairs:
            # no buffering so write is immediately available
            with tempfile.NamedTemporaryFile(buffering=0) as tmp_f:
                tmp_f.write(qasm_src.encode('utf8'))

                executables.set_current_option("QASM File Circuit")

                qreg = cirq.NamedQubit.range(0, n_qb, prefix="q_")

                executables.set_params_from_kwargs(file=tmp_f.name)

                exe = executables.get_current_option()
                circuit = exe()

                self.assertEqual(circuit, circuit_builder(qreg))


    def test_qasm_parsing(self):
        '''
            test the chunking of large qasm objects
        '''
        n_qb = 2000

        def generate_garbage_qasm():
            yield from itertools.chain(
                (
                    f"{g} q[{i}];" for g, i in itertools.product(
                        ("h", "rz(pi / 4)", "x",),
                        range(0, n_qb),
                    )
                ),
                (
                    f"CX q[{i}], q[{j}];" for i, j in zip(
                        range(0, n_qb -1), range(1, n_qb),
                    )
                )
            )

        qasm_prelude = f'''OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[{n_qb}];'''

        demo_qasm_src = '\n'.join([
            qasm_prelude,
            *(
                '\n'.join(v) for v in itertools.repeat(generate_garbage_qasm(), 10)
            )
        ])

        executables.set_current_option("QASM String Circuit")
        architectures.set_current_option("Rz Counter")
        LayoutProxy.add_layout_with_id(0, { "mem_bound": 1000, })

        qreg = cirq.NamedQubit.range(0, n_qb, prefix="q_")

        executables.set_params_from_kwargs(src=demo_qasm_src)

        compute_units = generate_compute_units(
            [0],
            architectures.get_current_option(),
            executables.get_current_option(),
        )

        # ensure everything isn't packed into a single compute unit
        self.assertTrue(len(list(compute_units)) > 1)



if __name__ == "__main__":
    unittest.main()

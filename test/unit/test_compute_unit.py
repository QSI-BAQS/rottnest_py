'''
    Testcases related to inspection/sanity for compute units
'''

import unittest

from cabaliser.operation_sequence import OperationSequence
from cabaliser import gates

from rottnest.compute_units.compute_unit import ComputeUnit

class TestComputeUnitSanity(unittest.TestCase):
    def test_default_compute_unit(self):
        cu = ComputeUnit("layout", unit_id="unit")
        self.assertEqual(cu.unit_id, "unit")
        self.assertEqual(cu.layout_id, "layout")
        self.assertEqual(cu.sequences, list())
        self.assertEqual(cu.memory_bound, None)
        self.assertEqual(cu.n_inputs, 0)
        self.assertEqual(cu.n_outputs, 0)
        self.assertEqual(cu.n_qubits, 0)
        self.assertEqual(cu.n_gates, 0)
        self.assertEqual(cu.n_rz_operations, 0)
        self.assertEqual(cu._qubit_labels, None)
        self.assertEqual(cu._rz_tracker_dict, None)

    def test_set_context(self):
        cu = ComputeUnit(0)
        cu.add_context(n_inputs=1, n_qubits=2, n_outputs=3, rz_tracker_dict={'a':1}, qubit_labels={'b':2})
        self.assertEqual(cu.n_inputs, 1)
        self.assertEqual(cu.n_qubits, 2)
        self.assertEqual(cu.n_outputs, 3)
        self.assertEqual(cu._rz_tracker_dict, {'a':1})
        self.assertEqual(cu._qubit_labels, {'b':2})

    def test_compute_unit_memory(self):
        for n_inputs in range(100):
            for n_rz_operations in range(100):
                cu = ComputeUnit(0)
                cu.n_inputs = n_inputs
                cu.n_rz_operations = n_rz_operations
                self.assertEqual(cu.curr_mem(), n_inputs * 2 + n_rz_operations)

    def test_compute_unit_auto_id(self):
        '''
            Ensures that (when set automatically) compute units are assigned different
            ids
        '''
        cu_a = ComputeUnit(0)
        cu_b = ComputeUnit(0)
        self.assertNotEqual(cu_a.unit_id, cu_b.unit_id)

    def test_export(self):
        '''
            Ensures that the exported information is correct
        '''
        cu = ComputeUnit(0)
        cu.add_context(n_inputs=1, n_qubits=2, n_outputs=3, rz_tracker_dict={}, qubit_labels={})

        self.assertEqual(cu.export(), {'n_inputs':1, 'n_outputs':3, 'n_qubits':2})


class TestComputeUnitSequencing(unittest.TestCase):
    '''
        Testcases related to sequencing Cabaliser objects with a ComputeUnit
        and ensuring that memory counting and circuit construction is correct
    '''
    def setUp(self):
        self.cu = ComputeUnit(0)


    def test_single_gate(self):
        ops = OperationSequence(1)
        ops.append(gates.H, 0)
        self.cu.append(ops)

        self.assertEqual(self.cu.n_gates, 1)
        self.assertEqual(self.cu.n_rz_operations, 0)
        self.assertEqual(len(self.cu), 1)

    def test_toffoli(self):
        # Rz tags
        _I_ = 0
        _T_ = 1
        _Tdag_ = 2

        def toffoli_gate(ctrl_a, ctrl_b, targ):
            return [
                (gates.RZ, (ctrl_a, _T_)),
                (gates.RZ, (ctrl_b, _T_)),
                (gates.H, (targ,)),
                (gates.CNOT, (ctrl_a, ctrl_b)),
                (gates.RZ, (targ, _T_)),
                (gates.CNOT, (ctrl_b, targ)),
                (gates.RZ, (ctrl_b, _Tdag_)),
                (gates.RZ, (targ, _T_)),
                (gates.CNOT, (ctrl_a, ctrl_b)),
                (gates.CNOT, (ctrl_b, targ)),
                (gates.CNOT, (ctrl_a, ctrl_b)),
                (gates.RZ, (targ, _Tdag_)),
                (gates.CNOT, (ctrl_b, targ)),
                (gates.CNOT, (ctrl_a, ctrl_b)),
                (gates.RZ, (targ, _Tdag_)),
                (gates.CNOT, (ctrl_b, targ)),
                (gates.H, (targ,))
            ]

        toffoli = toffoli_gate(0, 1, 2)
        ops = OperationSequence(len(toffoli))
        for opcode, args in toffoli:
            ops.append(opcode, *args)

        self.cu.append(ops)

        self.assertEqual(self.cu.n_gates, 17)
        self.assertEqual(self.cu.n_rz_operations, 7)
        self.assertEqual(len(self.cu), 1)

    def test_multiple_sequences(self):
        '''
            Ensure sequence counters work with multiple sequences
        '''
        ops = OperationSequence(1)
        ops.append(gates.H, 0)
        self.cu.append(ops)
        self.cu.append(ops)

        self.assertEqual(self.cu.n_gates, 2)
        self.assertEqual(self.cu.n_rz_operations, 0)
        self.assertEqual(len(self.cu), 2)

    def test_multiple_different_sequences(self):
        ops_a = OperationSequence(2)
        ops_a.append(gates.X, 0)
        ops_a.append(gates.RZ, 0, 0)

        ops_b = OperationSequence(3)
        ops_b.append(gates.Z, 0)
        ops_b.append(gates.RZ, 1, 1)
        ops_b.append(gates.CNOT, 0, 1)

        self.cu.append(ops_a)
        self.assertEqual(self.cu.n_gates, 2)
        self.assertEqual(self.cu.n_rz_operations, 1)
        self.assertEqual(len(self.cu), 1)

        self.cu.append(ops_b)
        self.assertEqual(self.cu.n_gates, 5)
        self.assertEqual(self.cu.n_rz_operations, 2)
        self.assertEqual(len(self.cu), 2)


if __name__ == "__main__":
    unittest.main()

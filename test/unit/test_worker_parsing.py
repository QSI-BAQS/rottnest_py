'''
    Testcases related to using an architecture to parse
    Cirq/Qualtran circuits
'''

import unittest
import cirq
import math

import qualtran.bloqs.basic_gates as qual_gates

# --[ Rottnest Imports ]---
from rottnest.plugins import executables, architectures
from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker
from rottnest.plugins.architecture_plugins import ArchitecturePlugins

from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.sequencer import Sequencer

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.interrupt import INTERRUPT

from rottnest.process_pool.standalone import process_elem_cache, process_elem_obj

# --[ Testing Utilities ]---
from utils.arch_factory import build_arch, build_worker, build_designer, build_composer

# Used to create qualtran circuits in a manner more similar to cirq
from utils.declarative_qualtran import build_bloq


class TestWorkerCircuitCounting(unittest.TestCase):
    '''
        Tests a worker that parses and "compiles" a circuit by counting
        the resulting gates
    '''
    def setUp(self):
        self.n_qubits = 100
        # Load n cirq qubits
        self.cirq_qubits = tuple(cirq.NamedQubit(str(x)) for x in range(self.n_qubits))
        # (circuit, n_gates) pairs to check
        # A correct result is when the compute units resulting from the parsing
        # of this circuit have n_gates in total

        # TODO : All gates, high rz that hits memory bound, more qubits
        self.circuits = [
            # --[ Cirq ]--
            (
                cirq.Circuit(cirq.H(self.cirq_qubits[0])),
                1
            ),
            (
                cirq.Circuit(
                    cirq.H(self.cirq_qubits[1]),
                    cirq.X(self.cirq_qubits[0])
                ),
                2
            ),
            (
                cirq.Circuit(
                    cirq.Y(self.cirq_qubits[0]),
                    cirq.Z(self.cirq_qubits[0]),
                    cirq.CNOT(self.cirq_qubits[0], self.cirq_qubits[1])
                ),
                3
            ),
            (
                cirq.Circuit(
                    cirq.X(self.cirq_qubits[0]) for i in range(100)
                ),
                100
            ),
            (
                cirq.Circuit(
                    cirq.Ry(rads=0.0)(self.cirq_qubits[0]),
                ),
                5        # TODO : Check that 5 actually expected here
            ),
            (
                cirq.Circuit(
                    cirq.H(self.cirq_qubits[0]),
                    cirq.measure(self.cirq_qubits[0])
                ),
                2
            ),
            # Toffoli
            (
                cirq.Circuit(
                    cirq.H(self.cirq_qubits[0]),
                    cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[0]),
                    cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[0]),
                    cirq.CNOT(self.cirq_qubits[2], self.cirq_qubits[0]),
                    cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[0]),
                    cirq.CNOT(self.cirq_qubits[2], self.cirq_qubits[0]),
                    cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[0]),
                    cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[0]),
                    cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[0]),
                    cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[2]),
                    cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[2]),
                    cirq.Rz(rads=math.pi / 4)(self.cirq_qubits[1]),
                    cirq.Rz(rads=-math.pi / 4)(self.cirq_qubits[2]),
                    cirq.CNOT(self.cirq_qubits[1], self.cirq_qubits[2]),
                    cirq.H(self.cirq_qubits[0])
                ),
                15
            ),
            (
                cirq.Circuit(
                    cirq.X(self.cirq_qubits[n]) for n in range(100)
                ),
                100
            ),
            # --[ Qualtran ]--
            # Note that the current Qualtran parsing uses the fact that `build_bloq` provides an object whose iterator
            # provides Cirq gates. This is NOT the standard function of an arbitrary Bloq
            (
                build_bloq(
                    registers = ('x',),
                    gates = [
                        (qual_gates.Hadamard(), {'q': 'x'})
                    ]
                ),
                1
            ),
            (
                build_bloq(
                    registers = ('x', 'y'),
                    gates = [
                        (qual_gates.Hadamard(), {'q': 'y'}),
                        (qual_gates.XGate(), {'q': 'x'})
                    ]
                ),
                2
            ),
            (
                build_bloq(
                    registers = ('x', 'y'),
                    gates = [
                        (qual_gates.YGate(), {'q': 'x'}),
                        (qual_gates.ZGate(), {'q': 'x'}),
                        (qual_gates.CNOT(), {'ctrl': 'x', 'target': 'y'})
                    ]
                ),
                3
            ),
            (
                build_bloq(
                    registers = ('x',),
                    gates = [
                        (qual_gates.XGate(), {'q': 'x'}) for i in range(100)
                    ]
                ),
                100
            ),
            (
                build_bloq(
                    registers = ('x',),
                    gates = [
                        (qual_gates.Ry(0.0), {'q': 'x'}),
                    ]
                ),
                5
            ),
            (
                build_bloq(
                    registers = ('x', 'y', 'z'),
                    gates = [
                        (qual_gates.Hadamard(), {'q': 'x'}),
                        (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'x'}),
                        (qual_gates.Rz(-math.pi / 4), {'q': 'x'}),
                        (qual_gates.CNOT(), {'ctrl': 'z', 'target': 'x'}),
                        (qual_gates.Rz(math.pi / 4), {'q': 'x'}),
                        (qual_gates.CNOT(), {'ctrl': 'z', 'target': 'x'}),
                        (qual_gates.Rz(-math.pi / 4), {'q': 'x'}),
                        (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'x'}),
                        (qual_gates.Rz(math.pi / 4), {'q': 'x'}),
                        (qual_gates.Rz(math.pi / 4), {'q': 'z'}),
                        (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'z'}),
                        (qual_gates.Rz(math.pi / 4), {'q': 'y'}),
                        (qual_gates.Rz(-math.pi / 4), {'q': 'z'}),
                        (qual_gates.CNOT(), {'ctrl': 'y', 'target': 'z'}),
                        (qual_gates.Hadamard(), {'q': 'z'})
                    ]
                ),
                15
            ),
        ]


    def test_circuit_n_gates(self):
        '''
            Test a worker that parses a circuit into a compute unit and counts the resulting gates
            directly
        '''
        # Create an architecture where the worker counts gates
        def count_gates(worker, compute_unit):
            '''
                Dummy worker inspects a compute unit
            '''
            # Count the gates in the compute_unit
            n_gates = sum(len(seq) for seq in compute_unit.sequences)
            worker.gate_ctr += n_gates
            return n_gates

        # Dummy architecture with;
        # - Designer memory bound drawn from layout
        # - Empty dummy composer
        # - Worker that uses the above `count_gates` method to count gates
        #   from a compute_unit (uses the `gate_ctr` property to store the count)
        arch = build_arch('WorkerGateCounting',
            build_designer('DummyDesigner', get_mem_bound=lambda s,l: l['mem_bound']),
            build_composer('DummyComposer'),
            build_worker('FullGateCtrWorker', gate_ctr=0, execute_compute_unit=count_gates),
        )

        # Pretend we actually loaded the architecture (just insert it in for now)
        architectures._options['WorkerGateCounting'] = arch
        architectures.set_current_architecture('WorkerGateCounting')

        layout_id = "circuit_n_gates_layout"
        # Load gates from a sequencer on a cirq object
        for circuit, answer in self.circuits:
            with self.subTest(circuit=circuit, answer=answer):
                # Instantiate a worker
                worker = arch.worker()
                # Create dummy layout and load it into the worker
                dummy_layout = {'mem_bound': 500}
                worker.load_layout(layout_id, dummy_layout)

                # Sequence the given circuit
                parser = PyliqtrParser(circuit)
                seq = Sequencer(layout_id)
                parser.parse()
                it = seq.sequence_pyliqtr(parser)

                for obj in it:
                    if obj != INTERRUPT:
                        # ^ Ignore cache events
                        # v Pass the sequenced sections of the parsed circuit to the
                        # worker
                        worker.execute_compute_unit(obj)

                self.assertEqual(worker.gate_ctr, answer)


    def test_circuit_n_gates_composed(self):
        '''
            Test an architecture where gates are counted by a composer
        '''
        def count_gates(worker, compute_unit):
            '''
                Dummy worker inspects a compute unit
            '''
            # Count the gates in the compute_unit
            n_gates = sum(len(seq) for seq in compute_unit.sequences)
            return {'n_gates': n_gates}

        class GateCtrResultsComposer(rottnest_composer.ResultsComposer):
            def __init__(self, result_dict=None, n_obj=1, comp_unit=None):
                super().__init__()

                if result_dict is None:
                    result_dict = {'n_gates': 0}

                self._obj = result_dict

            def __add__(self, other):
                res = GateCtrResultsComposer(result_dict={'n_gates': self._obj['n_gates'] + other._obj['n_gates']})
                res._unit_ids = self._unit_ids + other._unit_ids
                res._n_obj = self._n_obj + other._n_obj
                return res

            def __iadd__(self, other):
                self._unit_ids += other._unit_ids
                self._n_obj += other._n_obj
                self._obj['n_gates'] += other._obj['n_gates']
                return self


            def get_gate_count(self):
                return self._obj['n_gates']


        arch = build_arch('ComposedGateCounting',
            build_designer('DummyDesigner', get_mem_bound=lambda s, l : l['mem_bound']),
            build_composer('GateCtrComposer', results_composer_constructor=lambda s: GateCtrResultsComposer),
            build_worker('SingleGateCtrWorker', execute_compute_unit=count_gates)
        )

        # Pretend we actually loaded the architecture (just insert it in for now)
        architectures._options['ComposedGateCounting'] = arch
        architectures.set_current_architecture('ComposedGateCounting')

        layout_id = "composed_n_gates_layout"
        # Load gates from a sequencer on a cirq object
        for circuit, answer in self.circuits:
            with self.subTest(circuit=circuit, answer=answer):
                # Instantiate a worker and composer
                worker = arch.worker()
                # Create dummy layout and load it into the worker
                dummy_layout = {'mem_bound': 500}
                worker.load_layout(layout_id, dummy_layout)

                # Empty qubit tracker
                composer = arch.composer([dummy_layout], [])

                # Sequence the given circuit
                parser = PyliqtrParser(circuit)
                seq = Sequencer(layout_id)
                parser.parse()
                it = seq.sequence_pyliqtr(parser)

                res_composer = composer.results_composer_constructor()()

                for obj in it:
                    if obj != INTERRUPT:
                        # ^ Ignore cache events
                        # v Pass the sequenced sections of the parsed circuit to the
                        # worker
                        res = worker.execute_compute_unit(obj)
                        res_composer += composer.compose_result(obj.unit_id, res)

                self.assertEqual(res_composer.get_gate_count(), answer)


    def test_circuit_n_gates_composed_low_memory(self):
        '''
            Test an architecture where gates are counted by a composer,
            and there is a sufficiently low memory constraint
        '''
        # Set up worker and composer methods
        def count_gates(worker, compute_unit):
            '''
                Dummy worker inspects a compute unit
            '''
            # Count the gates in the compute_unit
            n_gates = sum(len(seq) for seq in compute_unit.sequences)
            return {'n_gates': n_gates}

        class GateCtrResultsComposer(rottnest_composer.ResultsComposer):
            def __init__(self, result_dict=None, n_obj=1, comp_unit=None):
                super().__init__()

                if result_dict is None:
                    result_dict = {'n_gates': 0}

                self._obj = result_dict

            def __add__(self, other):
                res = GateCtrResultsComposer(result_dict={'n_gates': self._obj['n_gates'] + other._obj['n_gates']})
                res._unit_ids = self._unit_ids + other._unit_ids
                res._n_obj = self._n_obj + other._n_obj
                return res

            def __iadd__(self, other):
                self._unit_ids += other._unit_ids
                self._n_obj += other._n_obj
                self._obj['n_gates'] += other._obj['n_gates']
                return self


            def get_gate_count(self):
                return self._obj['n_gates']


        arch = build_arch('ComposedGateCountingLowMem',
            build_designer('DummyDesigner', get_mem_bound=lambda s, l : l['mem_bound']),
            build_composer('GateCtrComposer', results_composer_constructor=lambda s: GateCtrResultsComposer),
            build_worker('SingleGateCtrWorker', execute_compute_unit=count_gates)
        )

        # Pretend we actually loaded the architecture (just insert it in for now)
        architectures._options['ComposedGateCountingLowMem'] = arch
        architectures.set_current_architecture('ComposedGateCountingLowMem')

        layout_id = "composed_n_gates_low_mem_layout"
        # Load gates from a sequencer on a cirq object
        for circuit, answer in self.circuits:
            with self.subTest(circuit=circuit, answer=answer):
                # Instantiate a worker and composer
                worker = arch.worker()
                # Create dummy layout and load it into the worker
                dummy_layout = {'mem_bound': 100}
                worker.load_layout(layout_id, dummy_layout)

                # Empty qubit tracker
                composer = arch.composer([dummy_layout], [])

                # Sequence the given circuit
                parser = PyliqtrParser(circuit)
                seq = Sequencer(layout_id)
                parser.parse()
                it = seq.sequence_pyliqtr(parser)

                res_composer = composer.results_composer_constructor()()

                for obj in it:
                    if obj != INTERRUPT:
                        # ^ Ignore cache events
                        # v Pass the sequenced sections of the parsed circuit to the
                        # worker
                        res = worker.execute_compute_unit(obj)
                        res_composer += composer.compose_result(obj.unit_id, res)

                self.assertEqual(res_composer.get_gate_count(), answer)


if __name__ == "__main__":
    unittest.main()

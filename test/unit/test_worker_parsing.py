'''
    Testcases related to using an architecture to parse
    Cirq/Qualtran circuits
'''

import unittest
import cirq
import math
import random
import sys

import qualtran.bloqs.basic_gates as qual_gates

# --[ Rottnest Imports ]---
from rottnest.plugins import executables, architectures
from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker
from rottnest.plugins.architecture_plugins import ArchitecturePlugins

from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.sequencer import Sequencer
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.interrupt import INTERRUPT

from rottnest.process_pool.standalone import process_elem_cache, process_elem_obj

# --[ Testing Utilities ]---
from functools import reduce

from utils.arch_factory import build_arch, build_worker, build_designer, build_composer

# Used to create qualtran circuits in a manner more similar to cirq
from utils.declarative_qualtran import build_bloq

# seed for testcases featuring randomisation
# if None, uses system time
RAND_SEED = None

# --[ Internal Utils ]--
def cirq_len(circuit):
    '''
        Determine the correct length for a given cirq circuit
        (accounting for internal wrapper sizes)
    '''
    lengths = {
        cirq.Rx: 3,
        cirq.Ry: 5
    }

    res = 0
    for moment in circuit.moments:
        for operation in moment:
            for t, v in lengths.items():
                if isinstance(operation.gate, t):
                    res += v
                    break
            else:
                res += 1

    return res


def qualtran_len(bloq):
    '''
        Determine the correct length for a given qualtran circuit
        (accounting for internal wrapper sizes)
    '''
    lengths = {
        qual_gates.Rx: 3,
        qual_gates.Ry: 5
    }

    res = 0
    for k, v in bloq.bloq_counts().items():
        for t, mult in lengths.items():
            if isinstance(k, t):
                res += v * mult
                break
        else:
            res += v

    return res


class TestWorkerCircuitCounting(unittest.TestCase):
    '''
        Tests a worker that parses and "compiles" a circuit by counting
        the resulting gates
    '''
    @classmethod
    def setUpClass(cls):
        '''
            Create a selection of useful architectures and their associated methods
        '''
        # -- Direct Counting --
        def count_gates_direct(worker, compute_unit):
            '''
                Direct gate counter to be used as a worker's "compilation" method
            '''
            # Count the gates in the compute_unit
            n_gates = reduce(lambda x, y: x + len(y), compute_unit.sequences, 0)
            worker.gate_ctr += n_gates


        direct_counter_arch = build_arch('DirectGateCounting',
            build_designer('DummyDesigner', get_mem_bound=lambda s,l: l['mem_bound']),
            build_composer('DummyComposer'),
            build_worker('FullGateCtrWorker', gate_ctr=0, execute_compute_unit=count_gates_direct),
        )

        architectures._options['DirectGateCounting'] = direct_counter_arch

        # -- Composed Counting --
        def count_gates_composed(worker, compute_unit):
            '''
                Gate counter that results in a composable description
            '''
            # Count the gates in the compute_unit
            n_gates = reduce(lambda x, y: x + len(y), compute_unit.sequences, 0)
            return {'n_gates': n_gates}

        class GateCtrResultsComposer(rottnest_composer.ResultsComposer):
            '''
                Results composer that combines gate counter descriptions
            '''
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

        composed_counter_arch = build_arch('ComposedGateCounting',
            build_designer('DummyDesigner', get_mem_bound=lambda s, l : l['mem_bound']),
            build_composer('GateCtrComposer', results_composer_constructor=lambda s: GateCtrResultsComposer),
            build_worker('SingleGateCtrWorker', execute_compute_unit=count_gates_composed)
        )

        architectures._options['ComposedGateCounting'] = composed_counter_arch

        '''
            Create a selection of useful layouts
        '''
        LayoutProxy.add_layout_with_id("std_layout", {'mem_bound': 500})
        LayoutProxy.add_layout_with_id("low_mem_layout", {'mem_bound': 50})

        '''
            Create circuits
        '''
        cls.n_qubits = 100
        # Load n cirq qubits
        cls.cirq_qubits = tuple(cirq.NamedQubit(str(x)) for x in range(cls.n_qubits))

        cls.cirq_circuits = [
            # ---[ Trivial Single Gates ]---
            cirq.Circuit(cirq.X(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.Y(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.Z(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.Rx(rads=0.0)(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.Ry(rads=0.0)(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.Rz(rads=0.0)(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.H(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.S(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.T(cls.cirq_qubits[0])),
            cirq.Circuit(cirq.CNOT(cls.cirq_qubits[0], cls.cirq_qubits[1])),
            cirq.Circuit(cirq.CZ(cls.cirq_qubits[0], cls.cirq_qubits[1])),

            cirq.Circuit(
                cirq.H(cls.cirq_qubits[1]),
                cirq.X(cls.cirq_qubits[0])
            ),

            cirq.Circuit(
                cirq.Y(cls.cirq_qubits[0]),
                cirq.Z(cls.cirq_qubits[0]),
                cirq.CNOT(cls.cirq_qubits[0], cls.cirq_qubits[1])
            ),

            cirq.Circuit(
                cirq.X(cls.cirq_qubits[0]) for i in range(100)
            ),

            cirq.Circuit(
                cirq.Ry(rads=0.0)(cls.cirq_qubits[0]),
            ),

            cirq.Circuit(
                cirq.H(cls.cirq_qubits[0]),
                cirq.measure(cls.cirq_qubits[0])
            ),

            # Toffoli
            cirq.Circuit(
                cirq.H(cls.cirq_qubits[0]),
                cirq.CNOT(cls.cirq_qubits[1], cls.cirq_qubits[0]),
                cirq.Rz(rads=-math.pi / 4)(cls.cirq_qubits[0]),
                cirq.CNOT(cls.cirq_qubits[2], cls.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(cls.cirq_qubits[0]),
                cirq.CNOT(cls.cirq_qubits[2], cls.cirq_qubits[0]),
                cirq.Rz(rads=-math.pi / 4)(cls.cirq_qubits[0]),
                cirq.CNOT(cls.cirq_qubits[1], cls.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(cls.cirq_qubits[0]),
                cirq.Rz(rads=math.pi / 4)(cls.cirq_qubits[2]),
                cirq.CNOT(cls.cirq_qubits[1], cls.cirq_qubits[2]),
                cirq.Rz(rads=math.pi / 4)(cls.cirq_qubits[1]),
                cirq.Rz(rads=-math.pi / 4)(cls.cirq_qubits[2]),
                cirq.CNOT(cls.cirq_qubits[1], cls.cirq_qubits[2]),
                cirq.H(cls.cirq_qubits[0])
            ),

            # Massive parameterised toffoli
            cirq.Circuit(
                reduce(lambda a, b: a + b,
                    (
                        [
                            cirq.H(qubit_0),
                            cirq.CNOT(qubit_1, qubit_0),
                            cirq.Rz(rads=-math.pi / 4)(qubit_0),
                            cirq.CNOT(qubit_2, qubit_0),
                            cirq.Rz(rads=math.pi / 4)(qubit_0),
                            cirq.CNOT(qubit_2, qubit_0),
                            cirq.Rz(rads=-math.pi / 4)(qubit_0),
                            cirq.CNOT(qubit_1, qubit_0),
                            cirq.Rz(rads=math.pi / 4)(qubit_0),
                            cirq.Rz(rads=math.pi / 4)(qubit_2),
                            cirq.CNOT(qubit_1, qubit_2),
                            cirq.Rz(rads=math.pi / 4)(qubit_1),
                            cirq.Rz(rads=-math.pi / 4)(qubit_2),
                            cirq.CNOT(qubit_1, qubit_2),
                            cirq.H(qubit_0)
                        ] for qubit_0, qubit_1, qubit_2 in zip(cls.cirq_qubits, cls.cirq_qubits[1:], cls.cirq_qubits[2:])
                    )
                )
            ),

            cirq.Circuit(
                cirq.X(cls.cirq_qubits[n]) for n in range(100)
            )
        ]

        cls.qualtran_circuits = [
            # Note that the current Qualtran parsing uses the fact that `build_bloq` provides an object whose iterator
            # provides Cirq gates. This is NOT the standard function of an arbitrary Bloq
            build_bloq(
                registers = ('x',),
                gates = [
                    (qual_gates.Hadamard(), {'q': 'x'})
                ]
            ),

            build_bloq(
                registers = ('x', 'y'),
                gates = [
                    (qual_gates.Hadamard(), {'q': 'y'}),
                    (qual_gates.XGate(), {'q': 'x'})
                ]
            ),

            build_bloq(
                registers = ('x', 'y'),
                gates = [
                    (qual_gates.YGate(), {'q': 'x'}),
                    (qual_gates.ZGate(), {'q': 'x'}),
                    (qual_gates.CNOT(), {'ctrl': 'x', 'target': 'y'})
                ]
            ),

            build_bloq(
                registers = ('x',),
                gates = [
                    (qual_gates.XGate(), {'q': 'x'}) for i in range(100)
                ]
            ),

            build_bloq(
                registers = ('x',),
                gates = [
                    (qual_gates.Ry(0.0), {'q': 'x'}),
                ]
            ),

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
        ]


    def test_cirq_direct_gate_count(self):
        '''
            Test a worker that parses a circuit (cirq) and directly counts the number of gates
        '''
        layout_id = "std_layout"
        architectures.set_current_architecture("DirectGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a cirq object
        for circuit in self.cirq_circuits:
            with self.subTest(circuit=circuit):
                # Reset the worker's counter
                worker.gate_ctr = 0

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

                self.assertEqual(worker.gate_ctr, cirq_len(circuit))


    def test_qualtran_direct_gate_count(self):
        '''
            Test a worker that parses a circuit (qualtran) and directly counts the number of gates
        '''
        layout_id = "std_layout"
        architectures.set_current_architecture("DirectGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a qualtran object
        for circuit in self.qualtran_circuits:
            with self.subTest(circuit=circuit):
                # Reset the worker's counter
                worker.gate_ctr = 0

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

                self.assertEqual(worker.gate_ctr, qualtran_len(circuit))


    def test_cirq_n_gates_composed(self):
        '''
            Test an architecture where gates are counted by a composer
        '''
        layout_id = "std_layout"
        architectures.set_current_architecture("ComposedGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a cirq object
        for circuit in self.cirq_circuits:
            with self.subTest(circuit=circuit):
                # Empty qubit tracker
                composer = arch.composer([LayoutProxy.get_layout(layout_id)], [])

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

                self.assertEqual(res_composer.get_gate_count(), cirq_len(circuit))


    def test_cirq_n_gates_composed_low_memory(self):
        '''
            Test an architecture where gates are counted by a composer,
            and there is a sufficiently low memory constraint
        '''
        layout_id = "low_mem_layout"
        architectures.set_current_architecture("ComposedGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a cirq object
        for circuit in self.cirq_circuits:
            with self.subTest(circuit=circuit):
                # Empty qubit tracker
                composer = arch.composer([LayoutProxy.get_layout(layout_id)], [])

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

                self.assertEqual(res_composer.get_gate_count(), cirq_len(circuit))


    def test_qualtran_n_gates_composed(self):
        '''
            Test an architecture where gates are counted by a composer
        '''
        layout_id = "std_layout"
        architectures.set_current_architecture("ComposedGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a qualtran object
        for circuit in self.qualtran_circuits:
            with self.subTest(circuit=circuit):
                # Empty qubit tracker
                composer = arch.composer([LayoutProxy.get_layout(layout_id)], [])

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

                self.assertEqual(res_composer.get_gate_count(), qualtran_len(circuit))


    def test_qualtran_n_gates_composed_low_memory(self):
        '''
            Test an architecture where gates are counted by a composer,
            and there is a sufficiently low memory constraint
        '''
        layout_id = "low_mem_layout"
        architectures.set_current_architecture("ComposedGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a qualtran object
        for circuit in self.qualtran_circuits:
            with self.subTest(circuit=circuit):
                # Empty qubit tracker
                composer = arch.composer([LayoutProxy.get_layout(layout_id)], [])

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

                self.assertEqual(res_composer.get_gate_count(), qualtran_len(circuit))


    def test_cirq_random_toffoli_low_memory(self):
        '''
            Randomised test over sequence of toffolis
        '''
        layout_id = "low_mem_layout"
        architectures.set_current_architecture("ComposedGateCounting")
        arch = architectures.get_current_architecture()

        if RAND_SEED is None:
            seed_v = random.randrange(sys.maxsize)
            print(f"--[ Seed for randomised Toffoli is {seed_v} ]--")
            random.seed(seed_v)
        else:
            random.seed(RAND_SEED)

        worker = arch.worker()

        circuit = cirq.Circuit(reduce(lambda a, b: a + b,
            (
                [
                    cirq.H(qubit_0),
                    cirq.CNOT(qubit_1, qubit_0),
                    cirq.Rz(rads=-math.pi / 4)(qubit_0),
                    cirq.CNOT(qubit_2, qubit_0),
                    cirq.Rz(rads=math.pi / 4)(qubit_0),
                    cirq.CNOT(qubit_2, qubit_0),
                    cirq.Rz(rads=-math.pi / 4)(qubit_0),
                    cirq.CNOT(qubit_1, qubit_0),
                    cirq.Rz(rads=math.pi / 4)(qubit_0),
                    cirq.Rz(rads=math.pi / 4)(qubit_2),
                    cirq.CNOT(qubit_1, qubit_2),
                    cirq.Rz(rads=math.pi / 4)(qubit_1),
                    cirq.Rz(rads=-math.pi / 4)(qubit_2),
                    cirq.CNOT(qubit_1, qubit_2),
                    cirq.H(qubit_0)
                ] for qubit_0, qubit_1, qubit_2 in (random.sample(self.cirq_qubits, 3) for i in range(1000))
            )
        ))

        composer = arch.composer(LayoutProxy.get_layout(layout_id), [])

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

        self.assertEqual(res_composer.get_gate_count(), cirq_len(circuit))




if __name__ == "__main__":
    unittest.main()

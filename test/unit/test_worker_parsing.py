'''
    Testcases related to using an architecture to parse
    Cirq/Qualtran circuits

    Tests both a trivial custom gate counting worker and
    the internal rz_collection worker
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

from rottnest.input_parsers.rz_tag_tracker import RzTagTracker

from rottnest.preprocessor.rz_collection_worker import RzCollectionWorker
from rottnest.preprocessor.rz_collection_composer import RzCollectionComposer, RzCollectionResultsComposer

# --[ Testing Utilities ]---
from functools import reduce

try:
    from utils.arch_factory import build_arch, build_worker, build_designer, build_composer
    from utils.quantum_lib_utils import cirq_len, qualtran_len, cirq_n_rz
    from test_data.circuit_data import cirq_circuits, cirq_qubits, qualtran_circuits
except ModuleNotFoundError:
    from .utils.arch_factory import build_arch, build_worker, build_designer, build_composer
    from .utils.quantum_lib_utils import cirq_len, qualtran_len, cirq_n_rz
    from .test_data.circuit_data import cirq_circuits, cirq_qubits, qualtran_circuits


# seed for testcases featuring randomisation
# if None, uses system time
RAND_SEED = None

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
    return compute_unit.unit_id, {'n_gates': n_gates}

class GateCtrResultsComposer(rottnest_composer.ResultsComposer):
    '''
        Results composer that combines gate counter descriptions
    '''
    def __init__(self, result_dict=None, n_obj=1, comp_unit=None, unit_id=None):
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


class TestWorkerCircuitCounting(unittest.TestCase):
    '''
        Tests a worker that parses and "compiles" a circuit by counting
        the resulting gates
    '''
    def test_cirq_direct_gate_count(self):
        '''
            Test a worker that parses a circuit (cirq) and directly counts the number of gates
        '''
        layout_id = "std_layout"
        architectures.set_current_architecture("DirectGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a cirq object
        for name, circuit in cirq_circuits.items():
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


    def test_cirq_n_gates_composed(self):
        '''
            Test an architecture where gates are counted by a composer
        '''
        layout_id = "std_layout"
        architectures.set_current_architecture("ComposedGateCounting")
        arch = architectures.get_current_architecture()

        worker = arch.worker()

        # Load gates from a sequencer on a cirq object
        for name, circuit in cirq_circuits.items():
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
                        unit_id, res = worker.execute_compute_unit(obj)
                        res_composer += composer.compose_result(unit_id, res)

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
        for name, circuit in cirq_circuits.items():
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
                        unit_id, res = worker.execute_compute_unit(obj)
                        res_composer += composer.compose_result(unit_id, res)

                self.assertEqual(res_composer.get_gate_count(), cirq_len(circuit))


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
                ] for qubit_0, qubit_1, qubit_2 in (random.sample(cirq_qubits, 3) for i in range(1000))
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
                unit_id, res = worker.execute_compute_unit(obj)
                res_composer += composer.compose_result(unit_id, res)

        self.assertEqual(res_composer.get_gate_count(), cirq_len(circuit))



class TestWorkerRzCollection(unittest.TestCase):
    def test_cirq_rz_collection(self):
        layout_id = "std_layout"

        worker = RzCollectionWorker()

        # Load gates from a sequencer on a cirq object
        for name, circuit in cirq_circuits.items():
            with self.subTest(circuit=circuit):
                composer = RzCollectionComposer(LayoutProxy.get_layout(layout_id), [])

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
                        unit_id, res = worker.execute_compute_unit(obj)
                        res_composer += composer.compose_result(unit_id, res)

                validation_count = cirq_n_rz(circuit)
                for angle, count in res_composer._obj.items():
                    self.assertEqual(
                        count,
                        validation_count[angle]
                    )


if __name__ == "__main__":
    unittest.main()

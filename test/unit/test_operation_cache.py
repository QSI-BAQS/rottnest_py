'''
    Testcases related to the caching of circuits
'''

import unittest
import cirq

from rottnest.plugins import executables, architectures

from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker

from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.sequencer import Sequencer
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED

from rottnest.monkey_patchers.pyliqtr_patcher import hash_function_patchers

from rottnest.rz_collector.rz_collection_worker import RzCollectionWorker
from rottnest.rz_collector.rz_collection_composer import RzCollectionComposer, RzCollectionResultsComposer

from utils.quantum_lib_utils import cirq_n_rz, cirq_circuit_to_gate
from test_data.test_circuits import cirq_circuits, cirq_qubits, qualtran_circuits

from utils.arch_factory import build_arch, build_designer


rz_collection_arch = build_arch("RzCollection",
    build_designer("DummyDesigner", get_mem_bound=lambda s,l: l['mem_bound']),
    RzCollectionComposer,
    RzCollectionWorker
)

architectures._options["RzCollection"] = rz_collection_arch

architectures.set_current_architecture("RzCollection")


class TestCachedRzCollection(unittest.TestCase):
    def test_cache_hit(self):
        '''
            Ensure that cache is hit with a cachable cirq circuit of toffolis
        '''
        layout = { 'mem_bound': 1000 }
        LayoutProxy.add_layout_with_id(0, layout)

        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3)
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: 3

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis into parser
        # TODO : wrap these in a decorator for ux
        PyliqtrParser.tracking_targets = [toffoli_gate_cls]
        hash_function_patchers[toffoli_gate_cls] = "DUMMY"

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(0)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        cache_hit = False

        for obj in it:
            if obj == INTERRUPT:
                cache_hit = True

        # Two interrupts for cache start and end + 24 requests
        self.assertTrue(cache_hit)


    def test_cache_composition(self):
        '''
            Ensure that result of composing over cache is the same as without composing
        '''
        layout = { 'mem_bound': 1000 }
        LayoutProxy.add_layout_with_id(0, layout)

        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3)
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: 3

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis into parser
        # TODO : wrap these in a decorator for ux
        PyliqtrParser.tracking_targets = [toffoli_gate_cls]
        hash_function_patchers[toffoli_gate_cls] = "DUMMY"

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(0)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        for obj in it:
            if obj == INTERRUPT:
                if obj.request_type == CACHED.START:
                    composer.cache_entry_start(obj)
                elif obj.request_type == CACHED.END:
                    composer.cache_entry_end(obj)
                elif obj.request_type == CACHED.REQUEST:
                    composer.cache_request(obj)
            else:
                composer.submit(obj)
                res = worker.execute_compute_unit(obj)
                composer.receive(obj.unit_id, res)

        self.assertEqual(composer.get_result()._obj["rz_counts"], cirq_n_rz(composed_toffoli_circuit))


    def test_cache_composition_mixed(self):
        '''
            Tests composition over cache with some cacheable and some primitive circuit
            components
        '''
        layout = { 'mem_bound': 1000 }
        LayoutProxy.add_layout_with_id(0, layout)

        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3)
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: 3


        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            cirq.X(cirq_qubits[0]),
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2])
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis into parser
        # TODO : wrap these in a decorator for ux
        PyliqtrParser.tracking_targets = [toffoli_gate_cls]
        hash_function_patchers[toffoli_gate_cls] = "DUMMY"

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(0)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        for obj in it:
            if obj == INTERRUPT:
                if obj.request_type == CACHED.START:
                    composer.cache_entry_start(obj)
                elif obj.request_type == CACHED.END:
                    composer.cache_entry_end(obj)
                elif obj.request_type == CACHED.REQUEST:
                    composer.cache_request(obj)
            else:
                composer.submit(obj)
                res = worker.execute_compute_unit(obj)
                composer.receive(obj.unit_id, res)

        self.assertEqual(composer.get_result()._obj["rz_counts"], cirq_n_rz(composed_toffoli_circuit))


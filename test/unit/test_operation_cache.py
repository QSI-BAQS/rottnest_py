'''
    Testcases related to the caching of circuits (without pandora)
'''

import unittest
import cirq

from Crypto.Hash import MD5

from rottnest.plugins import executables, architectures

from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker

from rottnest.compute_units.compute_unit import ComputeUnit
from rottnest.compute_units.sequencer import Sequencer
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser, rottnest_cacheable
from rottnest.input_parsers.interrupt import INTERRUPT, CACHED


from rottnest.architecture_interface.rottnest_composer import RottnestComposer

from rottnest_preprocessor.preprocessor.rz_collection_worker import RzCollectionWorker
from rottnest_preprocessor.preprocessor.rz_collection_composer import RzCollectionComposer, RzCollectionResultsComposer


# Ensure this works with both unittest and direct running
try:
    from utils.quantum_lib_utils import cirq_n_rz, cirq_circuit_to_gate
    from test_data.circuit_data import cirq_circuits, cirq_qubits, qualtran_circuits
    from utils.arch_factory import build_arch, build_designer
except ModuleNotFoundError:
    from .utils.quantum_lib_utils import cirq_n_rz, cirq_circuit_to_gate
    from .test_data.circuit_data import cirq_circuits, cirq_qubits, qualtran_circuits
    from .utils.arch_factory import build_arch, build_designer


mem_bound = "mem_bound"
default_mem_bound = 1000
layout_id = 0
generic_layout = { mem_bound: default_mem_bound }
LayoutProxy.add_layout_with_id(layout_id, generic_layout)

# Use the Rz Counter from the preprocessor
architectures.set_current_architecture("Rz Counter")


def const_hash(val):
    '''
        Simple cost fn
    '''
    def _wrap(*args, **kwargs):
        return val
    return _wrap

class TestCachedRzCollection(unittest.TestCase):
    def test_cache_hit(self):
        '''
            Ensure that cache is hit with a cacheable cirq circuit of toffolis
        '''
        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3)
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: 3

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        ), 3, name="ComposedToffoli")

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis into parser
        rottnest_cacheable(toffoli_gate_cls)

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        cache_hit = False

        for obj in it:
            if obj == INTERRUPT:
                cache_hit = True

        self.assertTrue(cache_hit)


    def test_cache_single_toffoli(self):
        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3)
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: 3

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2])
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2])
        )

        # Patch tracking of toffolis into parser
        rottnest_cacheable(toffoli_gate_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
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
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        self.assertEqual(composer.get_result()._obj, cirq_n_rz(composed_toffoli_circuit))


    def test_cache_composition(self):
        '''
            Ensure that result of composing over cache is the same as without composing
        '''
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
        rottnest_cacheable(toffoli_gate_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
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
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        self.assertEqual(composer.get_result()._obj, cirq_n_rz(composed_toffoli_circuit))


    def test_cache_composition_mixed(self):
        '''
            Tests composition over cache with some cacheable and some primitive circuit
            components
        '''
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
        rottnest_cacheable(toffoli_gate_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
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
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        self.assertEqual(composer.get_result()._obj, cirq_n_rz(composed_toffoli_circuit))


    def test_multi_cache_circuit(self):
        '''
            Tests a circuit with multiple distinct cacheable components
        '''
        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3)
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: 3

        # Convert existing single_rz circuit to a gate
        single_rz_cls = cirq_circuit_to_gate(cirq_circuits["single_rz"], 1)
        # Hash values again don't matter (just has to be different to the toffoli)
        single_rz_cls._rottnest_hash = lambda s, so: 5

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            single_rz_cls().on(cirq_qubits[0]),
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2])
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis and single_rz into parser
        rottnest_cacheable(toffoli_gate_cls)
        rottnest_cacheable(single_rz_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        seen_cache_hashes = set()

        for obj in it:
            if obj == INTERRUPT:
                seen_cache_hashes.add(obj.cache_hash())
                if obj.request_type == CACHED.START:
                    composer.cache_entry_start(obj)
                elif obj.request_type == CACHED.END:
                    composer.cache_entry_end(obj)
                elif obj.request_type == CACHED.REQUEST:
                    composer.cache_request(obj)
            else:
                composer.submit(obj)
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        # We expect to see the hashes for both the toffoli and the single rz
        self.assertEqual(len(seen_cache_hashes), 2)
        self.assertEqual(composer.get_result()._obj, cirq_n_rz(composed_toffoli_circuit))


    def test_circuit_multi_form(self):
        '''
            Tests a circuit composed of the same sub-circuit on different qubits (differnet cache hash)
        '''
        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3, name="ToffoliGate")
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: MD5.new(
            str(so.gate.__class__).encode('ascii')
            + b''.join(str(qb).encode('ascii') for qb in so.qubits)
        ).digest()

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            toffoli_gate_cls().on(cirq_qubits[2], cirq_qubits[1], cirq_qubits[0])
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis into parser
        rottnest_cacheable(toffoli_gate_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        seen_cache_hashes = set()

        for obj in it:
            if obj == INTERRUPT:
                seen_cache_hashes.add(obj.cache_hash())
                if obj.request_type == CACHED.START:
                    composer.cache_entry_start(obj)
                elif obj.request_type == CACHED.END:
                    composer.cache_entry_end(obj)
                elif obj.request_type == CACHED.REQUEST:
                    composer.cache_request(obj)
            else:
                composer.submit(obj)
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        # We have two forms of the cacheable toffoli, should see two distinct hashes
        # when accessing cache
        self.assertEqual(len(seen_cache_hashes), 2)
        self.assertEqual(composer.get_result()._obj, cirq_n_rz(composed_toffoli_circuit))


    def test_sequential_composition(self):
        '''
            Attempts to use the same composer for two cached compositions in a row
        '''
        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3, name="ToffoliGate")
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: MD5.new(
            str(so.gate.__class__).encode('ascii')
            + b''.join(str(qb).encode('ascii') for qb in so.qubits)
        ).digest()

        # NOTE : One layer of toffolis would be insufficient
        # as we hit an initial one-layer decomp
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            toffoli_gate_cls().on(cirq_qubits[2], cirq_qubits[1], cirq_qubits[0])
        ), 3)

        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]) for i in range(5)
        )

        # Patch tracking of toffolis into parser
        rottnest_cacheable(toffoli_gate_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(composed_toffoli_circuit)
        seq = Sequencer(layout_id)
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
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        self.assertEqual(composer.get_result()._obj, cirq_n_rz(composed_toffoli_circuit))

        composer.reset_result()

        longer_composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(
                cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]
            )
            for i in range(20)
        )

        parser = PyliqtrParser(longer_composed_toffoli_circuit)
        seq = Sequencer(layout_id)
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
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        self.assertEqual(composer.get_result()._obj, cirq_n_rz(longer_composed_toffoli_circuit))


    def test_circuit_vertical_cache(self):
        '''
            Tests a circuit composed of cacheable circuits that are themselves composed of cacheable circuits
        '''
        # Convert existing toffoli to a gate
        toffoli_gate_cls = cirq_circuit_to_gate(cirq_circuits["toffoli"], 3, name="ToffoliGate")
        # Hash value doesn't matter here as long as it
        # agrees for identical instances
        toffoli_gate_cls._rottnest_hash = lambda s, so: MD5.new(
            so.gate.name.encode('ascii')
            + b''.join(str(qb).encode('ascii') for qb in so.qubits)
        ).digest()

        # Convert composition of two toffolis into a gate
        composed_toffoli_gate_cls = cirq_circuit_to_gate(cirq.Circuit(
            toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            toffoli_gate_cls().on(cirq_qubits[2], cirq_qubits[1], cirq_qubits[0])
        ), 3, name="ComposedToffoliGate")
        composed_toffoli_gate_cls._rottnest_hash = lambda s, so: MD5.new(
            so.gate.name.encode('ascii')
            + b''.join(str(qb).encode('ascii') for qb in so.qubits)
        ).digest()

        # Convert composition of 2 composed toffolis into a gate
        composed_toffoli_circuit = cirq.Circuit(
            composed_toffoli_gate_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            composed_toffoli_gate_cls().on(cirq_qubits[2], cirq_qubits[1], cirq_qubits[0])
        )

        composed_toffoli_circuit_cls = cirq_circuit_to_gate(composed_toffoli_circuit, 3)

        # Compose the final result
        final_circuit = cirq.Circuit(
            composed_toffoli_circuit_cls().on(cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]),
            composed_toffoli_circuit_cls().on(cirq_qubits[1], cirq_qubits[0], cirq_qubits[2])
        )

        # Patch tracking of toffolis into parser
        rottnest_cacheable(toffoli_gate_cls)
        rottnest_cacheable(composed_toffoli_gate_cls)

        worker = RzCollectionWorker()
        composer = RzCollectionComposer((layout,), [cirq_qubits[0], cirq_qubits[1], cirq_qubits[2]])
        composer.reset_result()

        parser = PyliqtrParser(final_circuit)
        seq = Sequencer(layout_id)
        parser.parse()
        it = seq.sequence_pyliqtr(parser)

        seen_cache_hashes = set()

        for obj in it:
            if obj == INTERRUPT:
                seen_cache_hashes.add(obj.cache_hash())
                if obj.request_type == CACHED.START:
                    composer.cache_entry_start(obj)
                elif obj.request_type == CACHED.END:
                    composer.cache_entry_end(obj)
                elif obj.request_type == CACHED.REQUEST:
                    composer.cache_request(obj)
            else:
                composer.submit(obj)
                unit_id, res = worker.execute_compute_unit(obj)
                composer.receive(composer.compose_result(unit_id, res))

        # We have two forms of the cacheable toffoli,
        # per two forms of cacheable composed toffoli,
        # per two instances of said toffoli with different qubits
        # for 2^3 == 8
        self.assertEqual(len(seen_cache_hashes), 8)
        self.assertEqual(composer.get_result()._obj, cirq_n_rz(final_circuit))


if __name__ == "__main__":
    tst = TestCachedRzCollection()
    tst.test_cache_hit()
    #unittest.main()

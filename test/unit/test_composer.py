'''
    Tests the functionality of a composer and the stack frames it uses internally
    Ensures that deferred caching works as expected
'''

import unittest

from rottnest.architecture_interface.rottnest_composer import ComposerStackFrame, RottnestComposer, ResultsComposer, MemoryManager

# Patch over result composer get_tocks() so that it can be used as-is
ResultsComposer.get_tocks = lambda *a, **ka: 1

# Patch over result composer parallel compose so that it can be used as-is
def parallel_compose_results(self, other):
    self.__iadd__(other)
ResultsComposer.parallel_compose = parallel_compose_results

class MockComputeUnit():
    def __init__(self, unit_id, qubit_labels=dict()):
        self.unit_id = unit_id
        self._qubit_labels = qubit_labels

    def get_qubit_labels(self):
        return self._qubit_labels

class MockCachable():
    def __init__(self, cache_v, qubits=[]):
        self.cache_hash = lambda *a, **ka: cache_v
        self.op = type("DummyOp", (), dict(qubits=qubits))()
        self.non_participatory_qubits = 0

def unit_res_pair(res_obj, unit_id, qubit_labels=dict()):
    return (
        MockComputeUnit(unit_id, qubit_labels),
        ResultsComposer(res_obj, unit_id=unit_id)
    )

def generic_stack_frame(rottnest_hash=0):
    return ComposerStackFrame(rottnest_hash, ResultsComposer, {}, memory_manager=MemoryManager(ResultsComposer))

def generic_composer(composer_type=RottnestComposer):
    return composer_type({0:"dummy_layout"}, [])


class TestMemoryManagerFrame():
    COST_INIT = "INIT"
    COST_STORE = "STORE"
    COST_LOAD = "LOAD"
    COST_DELETE = "DELETE"
    COST_IDLE = "IDLE"
    def __init__(self, id):
        self.id = id
        self.costs = {
            TestMemoryManagerFrame.COST_INIT: 0,
            TestMemoryManagerFrame.COST_STORE: 0,
            TestMemoryManagerFrame.COST_LOAD: 0,
            TestMemoryManagerFrame.COST_DELETE: 0,
            TestMemoryManagerFrame.COST_IDLE: 0
        }

    def cost_labels(self, labels, cost_type):
        self.costs[cost_type] += len(labels)

    def cost_idle(self, n):
        self.costs[TestMemoryManagerFrame.COST_IDLE] += n


class TestMemoryManager(MemoryManager):
    def __init__(self, results_composer_constructor):
        self.ResultsComposer = results_composer_constructor
        self.frames = {}

    def frame_create(self, frame_id, labels):
        self.frames[frame_id] = TestMemoryManagerFrame(frame_id)
        self.frames[frame_id].cost_labels(labels, TestMemoryManagerFrame.COST_INIT)

    def frame_delete(self, frame_id, labels):
        self.frames[frame_id].cost_labels(labels, TestMemoryManagerFrame.COST_DELETE)

        res = self.ResultsComposer(self.frames[frame_id].costs)

        return res

    def store(self, frame_id, labels):
        self.frames[frame_id].cost_labels(labels, TestMemoryManagerFrame.COST_STORE)

    def load(self, frame_id, labels):
        self.frames[frame_id].cost_labels(labels, TestMemoryManagerFrame.COST_LOAD)

    def idle(self, frame_id, n_cycles):
        self.frames[frame_id].cost_idle(n_cycles)


class ComposerWithMemoryManager(RottnestComposer):
    @staticmethod
    def memory_manager_constructor():
        return TestMemoryManager



class StackFrameTests(unittest.TestCase):
    def test_frame_submit_recv_single(self):
        '''
            Ensure submitting a compute unit,
            and receiving a result works as expected
        '''
        frame = generic_stack_frame()

        unit, res = unit_res_pair({'val': 1}, 1, {1:'dummy qubit'})

        # Submit unit
        frame.submit(unit)

        # Inspect internals
        self.assertEqual(frame.n_submitted, 1)
        self.assertEqual(frame.qubit_map, {1:'dummy qubit'})
        self.assertEqual(frame.n_qubits_in_frame, 1)

        # Receive result
        frame.receive(res)

        self.assertEqual(frame.n_received, 1)
        # Inspect exposed result
        self.assertEqual(frame.get_result()._obj, res._obj)


    def test_frame_submit_recv_many(self):
        '''
            Ensure submitting mutliple compute units
            and receiving multiple results correclty
            aggregates them
        '''
        frame = generic_stack_frame()

        test_pairs = list(
            unit_res_pair({'val': i}, i, {1:'dummy qubit'}) for i in range(10)
        )

        expected_final_res = sum(range(10))

        expected_count = 1

        for pair in test_pairs:
            unit, res = pair

            # Submit unit
            frame.submit(unit)

            # Inspect internals
            self.assertEqual(frame.n_submitted, expected_count)

            # In this case, the qubit is always the same
            self.assertEqual(frame.qubit_map, {1:'dummy qubit'})
            self.assertEqual(frame.n_qubits_in_frame, 1)

            # Receive result
            frame.receive(res)

            self.assertEqual(frame.n_received, expected_count)

            expected_count += 1

        # Inspect exposed result
        self.assertEqual(frame.get_result()._obj['val'], expected_final_res)


    def test_frame_submit_recv_out_of_order(self):
        '''
            Ensure receiving results out of order
            does not impact composition
            Note that submit order does matter,
            but is to be guaranteed externally
        '''
        frame = generic_stack_frame()

        unit_count = 10

        # Submit everything first
        for i in range(1, unit_count + 1):
            frame.submit(MockComputeUnit(i))

        # Receive "last" result first
        frame.receive(ResultsComposer({'val': unit_count}, unit_id=unit_count))

        # Receive everything else
        for i in range(1, unit_count):
            frame.receive(ResultsComposer({'val': i}, unit_id=i))

        # Ensure exposed result is correct
        self.assertEqual(frame.get_result()._obj['val'], sum(range(1, unit_count + 1)))


    def test_frame_completion_check(self):
        '''
            Ensure that frame.complete() checks
            for;
            1. full submission
            2. full reception
        '''
        frame = generic_stack_frame()

        test_pairs = list(
            unit_res_pair({'val': i}, i, {1:'dummy qubit'}) for i in range(10)
        )

        # Submit and receive first five
        for pair in test_pairs[:5]:
            unit, res = pair

            frame.submit(unit)
            self.assertFalse(frame.complete())

            frame.receive(res)
            self.assertFalse(frame.complete())

        for pair in test_pairs[5:]:
            unit, res = pair

            frame.submit(unit)
            self.assertFalse(frame.complete())

        # Mark all as submitted
        frame.last_submitted()
        self.assertFalse(frame.complete())

        for pair in test_pairs[5:-1]:
            unit, res = pair
            frame.receive(res)
            self.assertFalse(frame.complete())

        final_unit, final_res = test_pairs[-1]

        frame.receive(final_res)
        self.assertTrue(frame.complete())


class CompositionTests(unittest.TestCase):
    def test_composer_submit_recv_single(self):
        '''
            Ensure submitting a compute unit, and receiving a result
            works as expected
        '''
        composer = generic_composer()
        composer.setup()

        unit, res = unit_res_pair({'val': 1}, 1, {1:'dummy qubit'})

        composer.submit(unit)
        composer.receive(res)

        self.assertEqual(composer.get_result()._obj, {'val': 1})


    def test_composer_submit_recv_many(self):
        '''
            Ensure submitting a sequence of compute units, and receiving the corresponding
            results works as expected (aggregtate final result)
        '''
        composer = generic_composer()
        composer.setup()

        test_pairs = list(
            unit_res_pair({'val': i}, i, {1:'dummy qubit'}) for i in range(10)
        )

        expected_final_res = sum(range(10))

        for pair in test_pairs:
            unit, res = pair

            composer.submit(unit)
            composer.receive(res)

        self.assertEqual(composer.get_result()._obj['val'], expected_final_res)


    def test_composer_submit_recv_out_of_order(self):
        '''
            Ensure that submitting a sequence of compute units, and receiving the
            corresponding results in a different order works as expected
        '''
        composer = generic_composer()
        composer.setup()

        unit_count = 10

        # Submit everything first
        for i in range(1, unit_count + 1):
            composer.submit(MockComputeUnit(i))

        # Receive "last" result first
        composer.receive(ResultsComposer({'val': unit_count}, unit_id=unit_count))

        # Receive everything else
        for i in range(1, unit_count):
            composer.receive(ResultsComposer({'val': i}, unit_id=i))

        # Ensure exposed result is correct
        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, unit_count + 1)))


    def test_composer_single_cache(self):
        '''
            Ensure that submitting to a single layer of vertical cache works
        '''
        composer = generic_composer()
        composer.setup()

        # Submit a misc. unit
        composer.submit(MockComputeUnit(1))
        composer.receive(ResultsComposer({'val': 1}, unit_id=1))

        # Start a cache layer
        cachable = MockCachable(1)

        composer.cache_entry_start(cachable)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(2, 10)):
            composer.submit(unit)
            composer.receive(res)

        composer.cache_entry_end(cachable)

        # Ensure exposed result is correct
        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 10)))


    def test_composer_horizontal_cache(self):
        '''
            Ensure that submitting to horizontal cache entries in a single layer works
        '''
        composer = generic_composer()
        composer.setup()

        first_cachable = MockCachable(1)

        composer.cache_entry_start(first_cachable)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(1, 10)):
            composer.submit(unit)
            composer.receive(res)

        composer.cache_entry_end(first_cachable)

        second_cachable = MockCachable(2)

        composer.cache_entry_start(second_cachable)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(10, 20)):
            composer.submit(unit)
            composer.receive(res)

        composer.cache_entry_end(second_cachable)

        # Ensure exposed result is correct
        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 20)))


    def test_composer_cache_request(self):
        '''
            Ensure that cache entries can be requested and are then aggregated
        '''
        composer = generic_composer()
        composer.setup()

        cachable = MockCachable(1)

        composer.cache_entry_start(cachable)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(1, 10)):
            composer.submit(unit)
            composer.receive(res)

        composer.cache_entry_end(cachable)

        composer.cache_request(cachable)

        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 10)) * 2)


    def test_composer_vertical_cache(self):
        '''
            Test vertical (nested) caching
        '''
        composer = generic_composer()
        composer.setup()

        outer_cachable = MockCachable(1)
        composer.cache_entry_start(outer_cachable)

        for i in range(10):
            composer.submit(MockComputeUnit(i))

        # Receive some of the results
        for i in range(5):
            composer.receive(ResultsComposer({'val': i}, unit_id=i))

        # Start another nested cachable
        inner_cachable = MockCachable(2)
        composer.cache_entry_start(inner_cachable)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(10, 20)):
            composer.submit(unit)
            composer.receive(res)

        composer.cache_entry_end(inner_cachable)

        # Receive remaining results
        for i in range(5, 10):
            composer.receive(ResultsComposer({'val': i}, unit_id=i))

        composer.cache_entry_end(outer_cachable)

        composer.cache_request(outer_cachable)

        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 20)) * 2)


    def test_composer_multi_layer_request(self):
        '''
            Test requesting an object that was cached at a different level

            ie.
                                A --- B      <- subsequently requested here
                                |
                             B --- B         <- populates cache here
        '''
        composer = generic_composer()
        composer.setup()

        a_cache = MockCachable('a')
        composer.cache_entry_start(a_cache)

        b_cache = MockCachable('b')
        composer.cache_entry_start(b_cache)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(10)):
            composer.submit(unit)
            composer.receive(res)

        composer.cache_entry_end(b_cache)

        composer.cache_request(b_cache)
        composer.cache_entry_end(a_cache)

        composer.cache_request(b_cache)

        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 10)) * 3)


    def test_deeply_nested_cache(self):
        '''
            Test deeply nested cache
        '''
        composer = generic_composer()
        composer.setup()

        cache_layers = []

        for i in range(10):
            cachable = MockCachable(i)
            composer.cache_entry_start(cachable)
            cache_layers.append(cachable)

        for unit, res in (unit_res_pair({'val': i}, i) for i in range(10)):
            composer.submit(unit)
            composer.receive(res)

        for i in range(10):
            cachable = cache_layers.pop()
            composer.cache_entry_end(cachable)

        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 10)))


    def test_cache_end_before_completion(self):
        '''
            Test receiving the end of cache interrupt before
            all corresponding results have been composed
        '''
        composer = generic_composer()
        composer.setup()

        test_pairs = list(unit_res_pair({'val': i}, i) for i in range(10))

        cachable = MockCachable(1)

        composer.cache_entry_start(cachable)

        for i in range(5):
            unit, res = test_pairs.pop()
            composer.submit(unit)
            composer.receive(res)

        # Remaining results aren't received immediately
        for unit, res in test_pairs:
            composer.submit(unit)

        composer.cache_entry_end(cachable)

        for unit, res in test_pairs:
            composer.receive(res)

        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 10)))


    def test_cache_request_deferred(self):
        '''
            Test completing a cache object, and requesting it,
            well before it is actually complete

                    A
                    |
                C - C - C

                    ^
                Cache population is only completed
                after the second C is requested
        '''
        composer = generic_composer()
        composer.setup()

        deferred_unit, deferred_res = unit_res_pair({'val': 1}, 1)

        cachable = MockCachable(1)

        composer.cache_entry_start(cachable)

        composer.submit(deferred_unit)
        for unit, res in (unit_res_pair({'val': i}, i) for i in range(2, 10)):
            composer.submit(unit)
            composer.receive(res)

        composer.all_submitted()

        composer.cache_entry_end(cachable)

        # Request before completion
        composer.cache_request(cachable)

        composer.receive(deferred_res)

        # Confirm that there are no outstanding deferences
        self.assertTrue(composer.complete())

        # Request after completion
        composer.cache_request(cachable)

        # Final result is 3x C
        self.assertEqual(composer.get_result()._obj['val'], 3 * sum(range(1, 10)))


    def test_cache_request_nested_defer(self):
        '''
            Tests layered deference of the form
            (lower denotes incomplete at time of cache end/hit,
            d is a non-cachable)

                    A
                    |
                b - B - c - d   (c completes after full submission)
                |   |
                c   c

            Where b = 50 + c, c = sum(range(1, 10), d = 1 + 2
                  a = 2b + c + d = 3c + 3 + 100
        '''
        composer = generic_composer()
        composer.setup()

        b_cachable = MockCachable('b')
        c_cachable = MockCachable('c')

        # Start b
        composer.cache_entry_start(b_cachable)

        # Submit 50 for b
        b_unit, b_res = unit_res_pair({'val': 50}, 50)

        composer.submit(b_unit)

        # Start c
        composer.cache_entry_start(c_cachable)

        # Submit all of c
        for i in range(10):
            composer.submit(MockComputeUnit(i))

        # Receive some of c
        for i in range(5):
            composer.receive(ResultsComposer({'val': i}, unit_id=i))

        # End c
        composer.cache_entry_end(c_cachable)

        self.assertFalse(composer.complete())

        # End b
        composer.cache_entry_end(b_cachable)

        self.assertFalse(composer.complete())

        # Request a b
        composer.cache_request(b_cachable)

        # Complete b (still waiting for c)
        composer.receive(b_res)

        self.assertFalse(composer.complete())

        # Request a c
        composer.cache_request(c_cachable)

        self.assertFalse(composer.complete())

        # Submit misc units making up a d
        composer.submit(MockComputeUnit(100))
        composer.receive(ResultsComposer({'val': 1}, unit_id=100))
        composer.submit(MockComputeUnit(101))
        composer.receive(ResultsComposer({'val': 2}, unit_id=101))

        composer.all_submitted()

        # Receive following c units
        for i in range(5, 10):
            composer.receive(ResultsComposer({'val': i}, unit_id=i))

        # Confirm that everything has resolved
        self.assertTrue(composer.complete())

        # Check the result
        self.assertEqual(composer.get_result()._obj['val'], 3 * sum(range(1, 10)) + 100 + 3)


    def test_cache_request_deeply_nested_defer(self):
        composer = generic_composer()
        composer.setup()

        deferred_unit, deferred_res = unit_res_pair({'val': 10}, 10)

        cache_layers = []

        for i in range(10):
            cachable = MockCachable(i)
            composer.cache_entry_start(cachable)
            cache_layers.append(cachable)

        composer.submit(deferred_unit)
        for unit, res in (unit_res_pair({'val': i}, i) for i in range(10)):
            composer.submit(unit)
            composer.receive(res)

        composer.all_submitted()

        for i in range(10):
            cachable = cache_layers.pop()
            composer.cache_entry_end(cachable)
            self.assertFalse(composer.complete())

        composer.receive(deferred_res)
        self.assertTrue(composer.complete())

        self.assertEqual(composer.get_result()._obj['val'], sum(range(1, 11)))


class MemoryManagerTests(unittest.TestCase):
    def test_memory_trivial_load_delete(self):
        '''
            Ensure trivial load and delete costs are incurred on cache start/end
        '''
        composer = generic_composer(ComposerWithMemoryManager)
        composer.setup()

        cachable = MockCachable(1, qubits=['a', 'b', 'c'])

        composer.cache_entry_start(cachable)

        unit, res = unit_res_pair({'val': 1}, 1)

        composer.submit(unit)
        composer.all_submitted()
        composer.receive(res)

        composer.cache_entry_end(cachable)

        self.assertTrue(composer.complete())

        res = composer.get_result()._obj

        # Three labels passed in
        self.assertEqual(res[TestMemoryManagerFrame.COST_INIT], 3)
        # Idle == calls to receive (as get_tocks is fixed at 1, and there's no layering)
        self.assertEqual(res[TestMemoryManagerFrame.COST_IDLE], 1)
        self.assertEqual(res[TestMemoryManagerFrame.COST_DELETE], 0)
        self.assertEqual(res[TestMemoryManagerFrame.COST_LOAD], 0)
        self.assertEqual(res[TestMemoryManagerFrame.COST_STORE], 0)


    def test_memory_load_delete_submit_qubits(self):
        '''
            Ensure a submit with some qubits actually associated is costed in memory
        '''
        composer = generic_composer(ComposerWithMemoryManager)
        composer.setup()

        cachable = MockCachable(1)

        composer.cache_entry_start(cachable)

        unit, res = unit_res_pair({'val': 1}, 1, qubit_labels={'a': 1, 'b': 2})

        composer.submit(unit)
        composer.all_submitted()
        composer.receive(res)

        composer.cache_entry_end(cachable)

        self.assertTrue(composer.complete())

        res = composer.get_result()._obj

        self.assertEqual(res[TestMemoryManagerFrame.COST_INIT], 0)
        # Idle == calls to receive (as above)
        self.assertEqual(res[TestMemoryManagerFrame.COST_IDLE], 1)
        self.assertEqual(res[TestMemoryManagerFrame.COST_DELETE], 0)
        # We incur load/store costs for the unit with 2 qubits above
        self.assertEqual(res[TestMemoryManagerFrame.COST_LOAD], 2)
        self.assertEqual(res[TestMemoryManagerFrame.COST_STORE], 2)


    def test_memory_multiple_submit(self):
        '''
            Ensure a sequence of submits are still costed properly
        '''
        composer = generic_composer(ComposerWithMemoryManager)
        composer.setup()

        cachable = MockCachable(1)

        composer.cache_entry_start(cachable)

        unit1, res1 = unit_res_pair({'val': 1}, 1, qubit_labels={'a': 1, 'b': 2})
        unit2, res2 = unit_res_pair({'val': 2}, 2, qubit_labels={'a': 2, 'b': 3})

        composer.submit(unit1)
        composer.submit(unit2)
        composer.all_submitted()
        composer.receive(res2)
        composer.receive(res1)

        composer.cache_entry_end(cachable)

        self.assertTrue(composer.complete())

        res = composer.get_result()._obj

        self.assertEqual(res[TestMemoryManagerFrame.COST_INIT], 0)
        # Idle == calls to receive (as above)
        self.assertEqual(res[TestMemoryManagerFrame.COST_IDLE], 2)
        self.assertEqual(res[TestMemoryManagerFrame.COST_DELETE], 0)
        # We incur load/store costs for the unit with 2 qubits above
        self.assertEqual(res[TestMemoryManagerFrame.COST_LOAD], 4)
        self.assertEqual(res[TestMemoryManagerFrame.COST_STORE], 4)


    def test_memory_multiple_cache(self):
        '''
            Ensure memory works correctly across multiple layers of cache
        '''
        composer = generic_composer(ComposerWithMemoryManager)
        composer.setup()

        cachable1 = MockCachable(1)
        cachable2 = MockCachable(2)

        composer.cache_entry_start(cachable1)

        unit1, res1 = unit_res_pair({'val': 1}, 1, qubit_labels={'a': 1, 'b': 2})
        unit2, res2 = unit_res_pair({'val': 2}, 2, qubit_labels={'a': 2, 'b': 3})

        composer.submit(unit1)

        composer.cache_entry_start(cachable2)

        composer.receive(res1)

        composer.submit(unit2)

        composer.all_submitted()

        composer.receive(res2)

        composer.cache_entry_end(cachable2)

        composer.cache_entry_end(cachable1)

        self.assertTrue(composer.complete())

        res = composer.get_result()._obj

        self.assertEqual(res[TestMemoryManagerFrame.COST_INIT], 0)
        # Idle == calls to receive + layer resolution
        self.assertEqual(res[TestMemoryManagerFrame.COST_IDLE], 3)
        self.assertEqual(res[TestMemoryManagerFrame.COST_DELETE], 0)
        # We incur load/store costs for 2x of the units with 2 qubits above
        self.assertEqual(res[TestMemoryManagerFrame.COST_LOAD], 4)
        self.assertEqual(res[TestMemoryManagerFrame.COST_STORE], 4)


    def test_memory_multiple_cache_with_requests(self):
        '''
            Ensure memory works correctly across multiple layers of cache,
            with cache requests
        '''
        composer = generic_composer(ComposerWithMemoryManager)
        composer.setup()

        cachable1 = MockCachable(1)
        cachable2 = MockCachable(2)

        composer.cache_entry_start(cachable1)

        unit1, res1 = unit_res_pair({'val': 1}, 1, qubit_labels={'a': 1, 'b': 2})
        unit2, res2 = unit_res_pair({'val': 2}, 2, qubit_labels={'a': 2, 'b': 3})

        composer.submit(unit1)

        composer.cache_entry_start(cachable2)

        composer.receive(res1)

        composer.submit(unit2)

        composer.all_submitted()

        composer.receive(res2)

        composer.cache_entry_end(cachable2)

        composer.cache_request(cachable2)

        composer.cache_entry_end(cachable1)

        self.assertTrue(composer.complete())

        res = composer.get_result()._obj

        self.assertEqual(res[TestMemoryManagerFrame.COST_INIT], 0)
        # Idle == calls to receive + layer resolution + cache request
        self.assertEqual(res[TestMemoryManagerFrame.COST_IDLE], 4)
        self.assertEqual(res[TestMemoryManagerFrame.COST_DELETE], 0)
        # We incur load/store costs for 4x of the units with 2 qubits above
        self.assertEqual(res[TestMemoryManagerFrame.COST_LOAD], 6)
        self.assertEqual(res[TestMemoryManagerFrame.COST_STORE], 6)


    def test_memory_multiple_cache_deferred(self):
        '''
            Ensure memory works correctly across multiple layers of cache,
            with cache requests and deference thereof
        '''
        composer = generic_composer(ComposerWithMemoryManager)
        composer.setup()

        cachable1 = MockCachable(1)
        cachable2 = MockCachable(2)

        composer.cache_entry_start(cachable1)

        unit1, res1 = unit_res_pair({'val': 1}, 1, qubit_labels={'a': 1, 'b': 2})
        unit2, res2 = unit_res_pair({'val': 2}, 2, qubit_labels={'a': 2, 'b': 3})

        composer.submit(unit1)

        composer.cache_entry_start(cachable2)

        composer.receive(res1)

        composer.submit(unit2)

        composer.all_submitted()

        composer.cache_entry_end(cachable2)

        composer.cache_request(cachable2)

        composer.cache_entry_end(cachable1)

        # Deferred receive
        composer.receive(res2)

        self.assertTrue(composer.complete())

        res = composer.get_result()._obj

        self.assertEqual(res[TestMemoryManagerFrame.COST_INIT], 0)
        # Idle == calls to receive + layer resolution + cache request
        self.assertEqual(res[TestMemoryManagerFrame.COST_IDLE], 4)
        self.assertEqual(res[TestMemoryManagerFrame.COST_DELETE], 0)
        # We incur load/store costs for 4x of the units with 2 qubits above
        self.assertEqual(res[TestMemoryManagerFrame.COST_LOAD], 6)
        self.assertEqual(res[TestMemoryManagerFrame.COST_STORE], 6)


if __name__ == "__main__":
    unittest.main()

import unittest

from rottnest.architecture_interface.rottnest_composer import ComposerStackFrame, RottnestComposer, ResultsComposer

# Patch over result composer get_tocks()
ResultsComposer.get_tocks = lambda *a, **ka: 1

class MockComputeUnit():
    def __init__(self, unit_id, qubit_labels=dict()):
        self.unit_id = unit_id
        self._qubit_labels = qubit_labels

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
    return ComposerStackFrame(rottnest_hash, ResultsComposer, {})

def generic_composer():
    return RottnestComposer({0:"dummy_layout"}, [])


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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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
        composer.reset_result()

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



if __name__ == "__main__":
    unittest.main()

'''
    Tests the base functionality of a rottnest worker
'''

import unittest

from rottnest.architecture_interface.rottnest_worker import RottnestWorker, PING, PONG, SET_RZ_PRECISION, EXEC_COMPUTE_UNIT, EXEC_GRAPH_STATE, GET_GRAPH, LOAD_LAYOUT, SHUTDOWN

from queue import Empty

def task(tsk, *args):
    return (tsk, args)

class MockQueue():
    def __init__(self, *contents):
        self.contents = list(contents)
        self.received = []

    def get(self, *a, **ka):
        '''
            ignores blocking/timeout
        '''
        if not self.contents:
            raise Empty("Mock queue is empty")
        item = self.contents.pop(0)
        # Exceptions (timeout, etc.) can be emulated by just adding
        # them to the list of contents on creation
        if isinstance(item, type) and issubclass(item, Exception):
            raise item()
        return item

    def put(self, item, *a, **ka):
        self.received.append(item)

    def get_received(self):
        return self.received

    def empty(self):
        return not bool(self.contents)


STEPPED_BOOLEAN_UNSET_SENTINEL = object()

def get_stepped_boolean(self):
    if self._stepped_boolean_count is STEPPED_BOOLEAN_UNSET_SENTINEL:
        return False
    if self._stepped_boolean_count <= 0:
        return False
    self._stepped_boolean_count -= 1
    return True

def get_stepped_boolean_or_err(self):
    if self._stepped_boolean_count is STEPPED_BOOLEAN_UNSET_SENTINEL:
        return False
    if self._stepped_boolean_count <= 0:
        raise Exception("Consumed stepped boolean on a loop, expected it to be unset")
    self._stepped_boolean_count -= 1
    return True

def set_stepped_boolean(self, v):
    if v is False:
        self._stepped_boolean_count = STEPPED_BOOLEAN_UNSET_SENTINEL


def rottnest_worker_set_loop_steps(n, err_on_elapse=False):
    # Dubious - now rather than looping as True forever, will be True n times, then False
    RottnestWorker.running = property(
        get_stepped_boolean if not err_on_elapse else get_stepped_boolean_or_err,
        set_stepped_boolean
    )
    RottnestWorker._stepped_boolean_count = n


class RottnestWorkerTest(unittest.TestCase):
    def test_startup_entrypoint(self):
        # We just want to start the worker
        rottnest_worker_set_loop_steps(1)

        task_queue = MockQueue()
        result_queue = MockQueue()
        comms_queue = MockQueue()

        RottnestWorker.entrypoint(
            task_queue,
            result_queue,
            comms_queue,
        )

    def test_startup_entrypoint_priority(self):
        # We just want to start the worker
        rottnest_worker_set_loop_steps(1)

        task_queue = MockQueue()
        result_queue = MockQueue()
        comms_queue = MockQueue()

        RottnestWorker.entrypoint(
            task_queue,
            result_queue,
            comms_queue,
            priority=True
        )

    def test_worker_shutdown(self):
        rottnest_worker_set_loop_steps(5, err_on_elapse=True)

        task_queue = MockQueue(task(SHUTDOWN))
        result_queue = MockQueue()
        comms_queue = MockQueue()

        RottnestWorker.entrypoint(
            task_queue,
            result_queue,
            comms_queue,
        )

    def test_ping_pong(self):
        rottnest_worker_set_loop_steps(5, err_on_elapse=True)

        task_queue = MockQueue(
            task(PING),
            task(SHUTDOWN)
        )
        result_queue = MockQueue()
        comms_queue = MockQueue()

        RottnestWorker.entrypoint(
            task_queue,
            result_queue,
            comms_queue,
        )

        self.assertTrue((PING, PONG) in result_queue.get_received(), f"Expected (PING <task>, PONG <result>), got {result_queue.get_received()} instead")

    def test_priority_ping_pong(self):
        rottnest_worker_set_loop_steps(5, err_on_elapse=True)

        task_queue = MockQueue(
            task(PING),
            task(SHUTDOWN)
        )
        result_queue = MockQueue()
        comms_queue = MockQueue()

        RottnestWorker.entrypoint(
            task_queue,
            result_queue,
            comms_queue,
            priority=True
        )

        self.assertTrue((PING, PONG) in result_queue.get_received(), f"Expected (PING <task>, PONG <result>), got {result_queue.get_received()} instead")


if __name__ == "__main__":
    unittest.main()

import unittest

from rottnest.architecture_interface.rottnest_worker import RottnestWorker
from rottnest.architecture_interface.rottnest_worker import PING, PONG, SET_PRECISION, EXEC_COMPUTE_UNIT, EXEC_GRAPH_STATE, GET_GRAPH, LOAD_LAYOUT


class MockWorkerQueue():
    def __init__(self, mock_get_v=None):
        self.mock_get_v = mock_get_v
        self.put_res = []

    def get(self):
        return self.mock_get_v

    def put(self, v):
        self.put_res.append(v)

    def inspect_put(self):
        res = self.put_res
        self.put_res = []
        return res


class TestWorkerSanity(unittest.TestCase):
    def testInit(self):
        '''
            Inspect an instantiated worker
        '''
        worker = RottnestWorker()
        self.assertEqual(worker.running, True)
        self.assertTrue(all(task in worker.worker_tasks for task in [PING, SET_PRECISION, EXEC_COMPUTE_UNIT, EXEC_GRAPH_STATE, GET_GRAPH, LOAD_LAYOUT]))


    def testInitBlind(self):
        '''
            Ensure that blind workers cannot GET_GRAPH
        '''
        worker = RottnestWorker(blind=True)
        self.assertEqual(worker.worker_tasks[GET_GRAPH], worker.not_supported)


    def testInitEntrypoint(self):
        '''
            Test spawning and entering a worker from the class entrypoint
        '''
        # Patch running from a raw attribute to a property that is True, then False
        running_states = [True, False]
        RottnestWorker.running = property(lambda s: running_states.pop(0), lambda s, v: None)
        mock_tasks = MockWorkerQueue((PING, ()))
        mock_responses = MockWorkerQueue()
        worker = RottnestWorker.entrypoint(mock_tasks, mock_responses)
        self.assertTrue(PONG in mock_responses.inspect_put())


    def testInitEntrypointBlind(self):
        '''
            Ensures that spawning a worker via entrypoint maintains blindness
            (inspected indirectly via a task)
        '''
        # Patch running from a raw attribute to a property that is True, then False
        running_states = [True, False]
        RottnestWorker.running = property(lambda s: running_states.pop(0), lambda s, v: None)
        mock_tasks = MockWorkerQueue((GET_GRAPH, ('fake_arg',)))
        mock_responses = MockWorkerQueue()
        RottnestWorker.entrypoint(mock_tasks, mock_responses, blind=True)
        self.assertTrue(RottnestWorker().not_supported() in mock_responses.inspect_put())

# TODO : Test worker tasks (many are currently NotImplemented?


if __name__ == "__main__":
    unittest.main()

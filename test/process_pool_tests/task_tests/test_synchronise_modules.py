import unittest

from rottnest import plugins
from rottnest.process_pool.tasks import SynchroniseModulesTask

from rottnest.test_utils.plugin_setup import setup_plugins
from rottnest.test_utils.proxy_pool_manager import ProxyPoolManager

class SynchroniseModulesTest(unittest.TestCase):


    def queue_introspection(self, mgr):
        assert not mgr.priority_task_queue.empty()
        res = mgr.priority_task_queue.get()
        assert res[0] == SynchroniseModulesTask.get_priority_worker_command()
        assert mgr.priority_task_queue.empty()


    def test_synch_modules(self):
        setup_plugins()

        mgr = ProxyPoolManager()

        SynchroniseModulesTask(
            pool_manager=mgr,
            module_keys=plugins.get_module_keys(),
        )
        self.queue_introspection(mgr)

if __name__ == '__main__':
    tst = SynchroniseModulesTest()
    tst.test_synch_modules()

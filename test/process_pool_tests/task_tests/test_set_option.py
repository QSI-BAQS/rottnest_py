import unittest

from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.tasks import SetOptionTask

from rottnest.test_utils.proxy_pool_manager import ProxyPoolManager
from rottnest.test_utils.plugin_setup import setup_plugins

from rottnest_preprocessor.preprocessor.architecture import PreprocessorArchitecture
from rottnest_error_budgets.error_budgets.even_distribution import EvenDistribution

from rottnest.test_utils.plugin_setup import setup_plugins_decorator
from rottnest.test_utils.layout_setup import setup_layout 

from rottnest import plugins

from rottnest.test_utils import SampleExecutable

class SetOptionTaskTest(unittest.TestCase):

    def queue_introspection(self, mgr):
        assert not mgr.priority_task_queue.empty()
        res = mgr.priority_task_queue.get()
        assert res[0] == SetOptionTask.get_priority_worker_command()
        assert mgr.priority_task_queue.empty()

    def test_example_executable(self):

        exe = SampleExecutable.get_name()
        setup_plugins(executable=exe)

        mgr = ProxyPoolManager()
        SetOptionTask(
            mgr,
            'rottnest_executables',
            SampleExecutable.get_name(),
            SampleExecutable.get_parameters(),
            None
        )
        self.queue_introspection(mgr)

    def test_architecture(self):
        mgr = ProxyPoolManager()

        SetOptionTask(
            mgr,
            'rottnest_architectures',
            PreprocessorArchitecture.get_name(),
            None
        )
        self.queue_introspection(mgr)

    def test_error_budgets(self):
        mgr = ProxyPoolManager()

        SetOptionTask(
            mgr,
            'rottnest_error_budgets',
            EvenDistribution.get_name(),
            None
        )
        self.queue_introspection(mgr)

    @setup_layout
    @setup_plugins_decorator()
    def test_pool_state(self):
        pool = get_pool()
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()

        # Synch pool state
        pool.synchronise()

        while None is (resp := pool.get_synchronisation_status()):
            pass
        pool_state = resp


        current_state = plugins.get_state() 
        for key in current_state: 
            assert current_state[key] == pool_state[key]

        pool.stop_workers()


if __name__ == '__main__':
    tst = SetOptionTaskTest()
    tst.test_example_executable()
    tst.test_error_budgets()
    tst.test_architecture()
    tst.test_pool_state()


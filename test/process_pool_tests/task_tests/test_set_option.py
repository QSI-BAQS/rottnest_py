import unittest

from rottnest.process_pool.tasks import set_option

from rottnest.test_utils.proxy_pool_manager import ProxyPoolManager

from rottnest_preprocessor.preprocessor.architecture import PreprocessorArchitecture
from rottnest_error_budgets.error_budgets.even_distribution import EvenDistribution

class SetOptionTaskTest(unittest.TestCase):

    def test_example_executable(self):
        # TODO: Update this to QASM when implemented 
        set_option.SetOptionTask()(
            ProxyPoolManager(),
            'rottnest_executables',
            'Fermi-Hubbard',
            None
        )

    def test_architecture(self):
        set_option.SetOptionTask()(
            ProxyPoolManager(),
            'rottnest_architectures',
            PreprocessorArchitecture.get_name(),
            None
        )


    def test_error_budgets(self):
        set_option.SetOptionTask()(
            ProxyPoolManager(),
            'rottnest_error_budgets',
            EvenDistribution.get_name(),
            None
        )





if __name__ == '__main__':
    tst = SetOptionTaskTest()
    tst.test_blank()

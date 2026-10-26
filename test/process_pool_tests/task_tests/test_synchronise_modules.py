import unittest

from rottnest.process_pool.tasks import synchronise_modules 
from rottnest.test_utils.proxy_pool_manager import ProxyPoolManager

class SetOptionTaskTest(unittest.TestCase):

    def test_synch_modules(self):

        synchronise_modules.SynchroniseModulesTask()(
            ProxyPoolManager(),
            {'rottnest_executables': [
                'Fermi-Hubbard',
                ]
            },
        )


if __name__ == '__main__':
    tst = SetOptionTaskTest()
    tst.test_synch_modules()

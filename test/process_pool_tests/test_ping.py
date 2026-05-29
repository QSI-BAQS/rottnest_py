'''
    Tests process pool execution
'''
import time

import unittest


# These workers have been tested without the pool elsewhere
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus

from rottnest.plugins import architectures, executables

from rottnest import test_utils
from rottnest.test_utils.executable import SampleExecutable


LAYOUT_ID = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(LAYOUT_ID, layout)

class ProcessPoolTests(unittest.TestCase):
    '''
        Process pool tests
    '''

    def test_ping(self):
        '''
            Tests ping through ipc
        '''

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(SampleExecutable.get_name())
        architectures.set_current_architecture(
            'Rz Counter'
        )

        pool = get_pool()
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()
        pool.terminate()



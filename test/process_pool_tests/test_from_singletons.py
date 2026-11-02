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

from rottnest.test_utils.plugin_setup import setup_plugins_decorator 


LAYOUT_ID = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(LAYOUT_ID, layout)

class ProcessPoolTests(unittest.TestCase):
    '''
        Process pool tests
    '''
    @setup_plugins_decorator()
    def test_process_pool_from_singletons(self):
        '''
            Tests executing the process pool with an Rz counter architecture
        '''

        pool = get_pool()
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()

        # Synch pool state
        pool.synchronise()

        # Start workers
        pool.start_workers()

        # Run the sequence
        pool.run_sequence([LAYOUT_ID])

        while pool.poll() != PoolStatus.FINISHED:
            # Example busy wait
            print("Executing...")
            time.sleep(1)

        # Shutdown the pool
        pool.terminate()
        return

if __name__ == '__main__':
    tst = ProcessPoolTests()
    tst.test_process_pool_from_singletons()
    #unittest.main()

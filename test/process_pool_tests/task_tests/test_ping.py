'''
    Tests process pool execution
'''
import time

import unittest

# These workers have been tested without the pool elsewhere

from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus


from rottnest.test_utils.plugin_setup import setup_plugins_decorator



class ProcessPoolTests(unittest.TestCase):
    '''
        Process pool tests
    '''

    def test_ping_manager(self):
        '''
            Tests ping through ipc
        '''
        pool = get_pool()
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()

    @setup_plugins_decorator()
    def test_ping_workers(self):
        '''
            Tests ping workers through ipc
        '''
        pool = get_pool()
        pool.start()

        ## Asserts correctness in here
        pool.ping_manager()

        ## Synch pool state
        pool.synchronise()

        ## Start workers
        pool.start_workers()

        ## Asserts correctness in here
        pool.ping_workers()

    def __del__(self):
        ## Shutdown
        pool.stop_workers()
        pool.terminate()

if __name__ == '__main__':
    tst = ProcessPoolTests()
    tst.test_ping_manager()
    tst.test_ping_workers()

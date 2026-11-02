'''
    Tests process pool execution
'''
import time

import unittest

# These workers have been tested without the pool elsewhere

from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus


from rottnest.test_utils.plugin_setup import setup_plugins_decorator
from rottnest.test_utils.layout_setup import setup_layout 


class CallgraphTests(unittest.TestCase):
    '''
        Process pool tests
    '''

    @setup_layout
    @setup_plugins_decorator()
    def test_get_root(self):
        '''
            Tests ping workers through ipc
        '''
        pool = get_pool()
        pool.start()
        pool.synchronise()

        ### Asserts correctness in here
        pool.get_callgraph(None)

        while None is (
                resp := pool.get_callgraph_status()
            ):
            pass
        print("RES", resp)
        pool.terminate()

        
if __name__ == '__main__':
    tst = CallgraphTests()
    tst.test_get_root()

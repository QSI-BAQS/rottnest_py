'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables

import unittest

from rottnest import test_utils

from rottnest.process_pool.singleton import get_pool

class ErrorTargetProcedureTest(unittest.TestCase):

    # TODO
    def test_asynch(self):
        '''
            Checks that asynch is collected properly
        '''
        pool = get_pool()
        procedure = pool.PoolProcedure()
        assert not procedure.is_asynchronous()


if __name__ == '__main__':
    #tst = ErrorTargetProcedureTest()

    unittest.main()

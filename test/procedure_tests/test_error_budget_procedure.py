'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables

import unittest

#from rottnest.procedures import error_budget 

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils
from rottnest.test_utils.plugin_support import add_executable, add_architecture

class ErrorTargetProcedureTest(unittest.TestCase):

    # TODO
    def test_asynch(self):
        '''
            Checks that asynch is collected properly
        '''

        procedure = pool.PoolProcedure()
        assert not procedure.is_asynchronous()




if __name__ == '__main__':
    #tst = ErrorTargetProcedureTest()

    unittest.main()

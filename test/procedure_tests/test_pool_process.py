'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables
print("LOADED")


import unittest

from rottnest.procedures import pool
from rottnest.procedures import stage

#from rottnest.plugins import architectures, executables

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils
from rottnest.test_utils.plugin_support import add_executable, add_architecture

class PoolProcedureTest(unittest.TestCase):


    def test_asynch(self):
        '''
            Checks that asynch is collected properly
        '''

        procedure = pool.PoolProcedure()
        assert procedure.is_asynchronous()


    def test_full_run(self):

        # Setup the pool
        architectures.set_current_architecture(
            'Rz Counter' 
        )

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(
            SampleExecutable.get_name() 
        )

        procedure = pool.PoolProcedure()
        procedure.execute()

        while not procedure.complete():
            procedure.poll()


if __name__ == '__main__':
    tst = PoolProcedureTest()
    tst.test_full_run()

    #unittest.main()


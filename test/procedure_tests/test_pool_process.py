'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables

import unittest

from rottnest.procedures import pool
from rottnest.procedures import stage

#from rottnest.plugins import architectures, executables
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils

class PoolProcedureTest(unittest.TestCase):


    def test_asynch(self):
        '''
            Checks that asynch is collected properly
        '''

        procedure = pool.PoolProcedure()
        assert procedure.is_asynchronous()


    def test_full_run(self):

        layout_id = 0
        memory_bound = 1000
        layout = {'mem_bound': memory_bound}
        LayoutProxy.add_layout_with_id(layout_id, layout)

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

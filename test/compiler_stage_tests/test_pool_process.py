'''
    Tests pool process
'''

import unittest

from rottnest.compilation_procedures import pool
from rottnest.compilation_procedures import stage

from rottnest.test_utils.executable import SampleExecutable 

 
class PoolProcedureTest(unittest.TestCase):


    def test_full_run(self):
        procedure = pool.PoolProcedure()
        procedure.execute()



if __name__ == '__main__':
    unittest.main()

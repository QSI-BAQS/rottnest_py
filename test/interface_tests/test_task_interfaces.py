'''
    Tests the implementation of all stages
'''

import importlib

import unittest
from parameterized import parameterized as parameterised

from rottnest.process_pool import tasks
from rottnest.test_utils.recurse_package import recurse_package

class TaskInterfaceTest(unittest.TestCase):
    '''
        Tests implementations of stages
        These should simply not throw errors on class creation
        This is triggered on import 
    '''
    @parameterised.expand(
        recurse_package(tasks) 
    )
    def test_file(self, path, package):
        '''
            Load the python module from a path
        '''
        # Assert triggered on import
        _ = importlib.import_module(path, package)
          

if __name__ == '__main__':
    unittest.main()

'''
    Tests the implementation of all stages
'''

import os
import importlib, pkgutil
from typing import Iterable

import unittest
from parameterized import parameterized as parameterised

from rottnest import procedures
from rottnest.test_utils.recurse_package import recurse_package

class StageInterfaceTest(unittest.TestCase):
    '''
        Tests implementations of stages
        These should simply not throw errors on class creation
        This is triggered on import 
    '''
    @parameterised.expand(
        recurse_package(procedures) 
    )
    def test_file(self, path, package):
        '''
            Load the python module from a path
        '''
        # Assert triggered on import
        _ = importlib.import_module(path, package)
          

if __name__ == '__main__':
    unittest.main()

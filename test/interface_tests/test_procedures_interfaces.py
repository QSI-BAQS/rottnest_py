'''
    Tests the implementation of all stages
'''

import os
import importlib, pkgutil
from typing import Iterable

import unittest
from parameterized import parameterized as parameterised

from rottnest import procedures

def recurse_package(base_module: "module") -> Iterable[tuple["str", "package"]]:
    '''
        Generates all python files in the procedures directory
    '''
    for module in pkgutil.iter_modules(base_module.__path__):
        if not module.ispkg:
            yield (f'.{module.name}', base_module.__package__)

        else:
            submodule = importlib.import_module(f'.{module.name}', base_module.__package__)
            yield from recurse_package(submodule)

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

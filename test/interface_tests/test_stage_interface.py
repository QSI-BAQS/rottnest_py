'''
    Tests the implementation of all stages
'''

import os
import importlib, pkgutil
from typing import Iterable

import unittest
from parameterized import parameterized as parameterised

from rottnest import procedures

def procedures_files() -> Iterable[str]:
    '''
        Generates all python files in the procedures directory
    '''
    first = True 
    for path, _, files in os.walk(procedures.__path__[0]):

        # Skip the top level directory
        if first:
            first = False
            continue

        for file in files:
            # Only select python files
            if file[-3:] != '.py' or file == '__init__.py':
                continue
            full_path = f'{path}/{file}'
            yield path, full_path

class StageInterfaceTests(unittest.TestCase):
    '''
        Tests implementations of stages
        These should simply not throw errors on class creation
        This is triggered on import 
    '''
    @parameterised.expand(
        procedures_files()
    )
    def test_file(self, path, file):
        '''
            Load the python module from a path
        '''
        spec = importlib.util.spec_from_file_location('test', file, submodule_search_locations=path )
        if spec is None:
            return 
        module = importlib.util.module_from_spec(spec)
        # On exec triggers the compilation of the class
        # and the validation of the interface
        spec.loader.exec_module(module)
          

if __name__ == '__main__':
    unittest.main()

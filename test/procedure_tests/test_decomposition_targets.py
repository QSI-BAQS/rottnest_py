import unittest 

from rottnest import test_utils
from rottnest.test_utils.executable import SampleExecutable

from rottnest.plugins import executables
from rottnest.executables import executable

from rottnest.procedures.decomposition_patchers import stage_decomposition_patchers
from rottnest.monkey_patchers import get_hash_patcher, load_hash_patcher, clear_hash_patcher


def class_builder():
    '''
        Helper builder function that makes new class instances
    '''
    class Blank:
        '''
            Test helper class
            Object to inject fields on
        '''
        ...
    return Blank

def fn(*args, **kwargs):
    '''
        Test helper function 
        Acts as a proxy hash function
    '''
    ...

def collector(*args, **kwargs):
    '''
        Test helper function
        Acts as a proxy for a map from classes to hashes 
    '''
    return {class_builder(): fn}


class TestPatchers(unittest.TestCase):
    '''
        Tests the hash patchers
    '''
    def test_null_patchers(self):

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(
            SampleExecutable.get_name() 
        )

        clear_hash_patcher() 
        patcher = get_hash_patcher()
        initial_hashes = len(patcher) 
 
        assert 0 == initial_hashes 

        # Nothing loaded, should null 
        stage = stage_decomposition_patchers.DecomposerPatchStage()
        stage.execute(None)

        assert len(patcher) > initial_hashes

    def test_add_patchers(self):
        '''
            Tests that a pyliqtr hash can be added
        '''
        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(
            SampleExecutable.get_name() 
        )

        SampleExecutable.pyliqtr_patchers = collector
 
        patcher = load_hash_patcher()
        initial_hashes = len(patcher) 
 
        # Nothing loaded, should null 
        stage = stage_decomposition_patchers.DecomposerPatchStage()
        stage.execute(None)

        assert len(patcher) == initial_hashes + 1 


if __name__ == '__main__':
    unittest.main()

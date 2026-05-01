'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables

import unittest

from rottnest.procedures import preprocess_and_execute 
from rottnest_preprocessor import PreprocessorArchitecture

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils
from rottnest.test_utils.plugin_support import add_executable, add_architecture

from rottnest.process_pool import get_pool

class PreprocessorProcedureTest(unittest.TestCase):

    def test_full_run(self):

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(
            SampleExecutable.get_name() 
        )
        architectures.set_current_architecture(PreprocessorArchitecture.get_name())

        procedure = preprocess_and_execute.PreprocAndExecuteProcedure(reporting=False)
        procedure.execute()

        while not procedure.complete():
            procedure.poll()

        assert procedure.preprocessor.get_rz_count() == 1680 
        assert procedure.preprocessor.set_rz_precision() == 20 
        assert procedure.preprocessor.get_t_count() == 1680 
        self.term()

    def term(self):
        pool = get_pool()
        pool.terminate()


if __name__ == '__main__':
    tst = PreprocessorProcedureTest()
    tst.test_full_run()
    #unittest.main()


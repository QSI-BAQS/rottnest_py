'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables

import unittest

from rottnest.procedures import preprocess_and_execute 

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils
from rottnest.test_utils.plugin_support import add_executable, add_architecture


class PreprocessorProcedureTest(unittest.TestCase):

    def test_full_run(self):

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(
            SampleExecutable.get_name() 
        )

        procedure = preprocess_and_execute.PreprocAndExecuteProcedure()
        procedure.execute()

        while not procedure.complete():
            procedure.poll()

        assert procedure.preprocessor.get_rz_count() == 1680 
        assert procedure.preprocessor.set_rz_precision() == 20 
        assert procedure.preprocessor.get_t_count() == 1680 

        #print(procedure.get_t_infidelity())


if __name__ == '__main__':
    tst = PreprocessorProcedureTest()
    tst.test_full_run()

    #unittest.main()


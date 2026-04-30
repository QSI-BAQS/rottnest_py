'''
    Tests pool process
'''
from rottnest.plugins import architectures, executables


import unittest

from rottnest.procedures import preprocessor 
from rottnest.procedures import stage

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils
from rottnest.test_utils.plugin_support import add_executable, add_architecture
from rottnest.process_pool import terminate_pool

class PreprocessorProcedureTest(unittest.TestCase):

    def test_full_run(self):

        executables.load_modules_from_strings(test_utils.__file__)

        executables.set_current_executable(
            SampleExecutable.get_name() 
        )
        architectures.set_current_architecture( 
            'Rz Counter'
        )

        procedure = preprocessor.PreprocessorProcedure()
        procedure.execute()

        while not procedure.complete():
            procedure.poll()

        assert procedure.get_rz_count() == 1680 
        assert procedure.set_rz_precision() == 20 
        assert procedure.get_t_count() == 1680 

        #print(procedure.get_t_infidelity())

        terminate_pool()

if __name__ == '__main__':
    tst = PreprocessorProcedureTest()
    tst.test_full_run()

    #unittest.main()


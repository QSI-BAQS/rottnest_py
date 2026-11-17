import unittest
from rottnest.procedures.procedure_manager import ProcedureManagerSelector
from rottnest.server.app.application import RottnestApplication

from rottnest.plugins import architectures, executables

import unittest

from rottnest.procedures import preprocess_and_execute 
from rottnest_preprocessor import PreprocessorArchitecture

from rottnest.test_utils.executable import SampleExecutable 

from rottnest import test_utils
from rottnest.test_utils.plugin_support import add_executable, add_architecture

from rottnest.procedures import procedure, stage, exceptions

import time

class ProcedureManagerTest(unittest.TestCase):

    def test_preproc_and_execute(self):
        '''
            Aim is to stack a number of procedures and execute them
            in sequence using the defer method and explicit dequeuing
        '''
        # TODO: Argument is pointless
        #procman = ProcedureManager(RottnestApplication.get_uninitialised_instance())


        # Setup environment
        executables.load_modules_from_strings(
            test_utils.__file__
        )
        executables.set_current_option(
            SampleExecutable.get_name() 
        )
        architectures.set_current_option(
            PreprocessorArchitecture.get_name()
        )

        manager_selector = ProcedureManagerSelector.get_instance()
        procman = manager_selector.get_concurrent_manager(None)
        procman.execute(procedure)

        #handler = procman.start_concurrent_manager_in_thread()

        #procman.stop_manager()
        #handler.join()

        i = 0
        while procman.get_enqueued_size() > 0: 
            i += 1
            time.sleep(1)


if __name__ == '__main__':
    unittest.main()
    # tobj = ProcedureManagerTest()
    # tobj.test_single_procedure_enqueue()


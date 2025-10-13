'''
    Testcases related to the creation, importing and basic use of architectures
'''

import unittest

from typing import Type, Callable

# --[ Rottnest Imports ]---
from rottnest.plugins import executables, architectures
from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker
from rottnest.plugins.architecture_plugins import ArchitecturePlugins

# --[ Testing Utilities ]---
# Used to test architecture imports
from dummy_arch.dummy_arch import DummyWorker, DummyDesigner, DummyComposer


# TODO : Test the loaders used below
class TestModuleLoading(unittest.TestCase):
    '''
        Testcases related to loading modules (providing architectures)
    '''
    def testModuleFromString(self):
        archPlugins = ArchitecturePlugins()
        module = archPlugins._load_module_from_module_string("dummy_arch")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testModuleFromPath(self):
        archPlugins = ArchitecturePlugins()
        module = archPlugins._load_module_from_file_path("./standalone.py")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testModuleFromConfigFile(self):
        archPlugins = ArchitecturePlugins()
        module = archPlugins._load_modules_from_config("./module.conf")[0]
        self.assertEqual(len(module.rottnest_architectures), 1)


class TestDummyStringImportedArchitecture(unittest.TestCase):
    '''
        Testcases related to the bare minimum inspection of an architecture
        loaded as a plugin via a string
        (ensure that getters and attributes expose the correct things)
    '''
    def setUp(self):
        self.archPlugins = ArchitecturePlugins()
        # Acquire a module and load it into the ArchitecturePlugins
        module = self.archPlugins._load_module_from_module_string("dummy_arch")
        self.archPlugins._modules.add(module)
        self.archPlugins.load_options_from_modules()
        self.arch = self.archPlugins['Dummy']

    def testArchCount(self):
        self.assertEqual(len(self.archPlugins._modules), 1)
        self.assertEqual(len(self.archPlugins.get_architectures()), 1)

    def testGetName(self):
        self.assertEqual(self.arch.get_name(), "Dummy")

    def testGetWorkerEntry(self):
        self.assertTrue(isinstance(self.arch.worker_entrypoint(), Callable))

    def testWorkerEntryMatches(self):
        self.assertEqual(self.arch.worker_entrypoint(), self.arch.worker.entrypoint)

    def testInstantiateWorker(self):
        self.assertTrue(isinstance(self.arch.worker(), DummyWorker))

    def testInstantiateDesigner(self):
        self.assertTrue(isinstance(self.arch.designer(), DummyDesigner))

    def testInstantiateComposer(self):
        self.assertTrue(isinstance(self.arch.composer([ ], [ ]), DummyComposer))


class TestDummyPathImportedArchitecture(unittest.TestCase):
    '''
        Testcases matching above, but for an architecture loaded
        from a path
    '''
    def setUp(self):
        self.archPlugins = ArchitecturePlugins()
        # Acquire a module and load it into the ArchitecturePlugins
        module = self.archPlugins._load_module_from_file_path("./standalone.py")
        self.archPlugins._modules.add(module)
        self.archPlugins.load_options_from_modules()
        self.arch = self.archPlugins['Dummy']

    def testArchCount(self):
        self.assertEqual(len(self.archPlugins._modules), 1)
        self.assertEqual(len(self.archPlugins.get_architectures()), 1)

    def testGetName(self):
        self.assertEqual(self.arch.get_name(), "Dummy")

    def testGetWorkerEntry(self):
        self.assertTrue(isinstance(self.arch.worker_entrypoint(), Callable))

    def testWorkerEntryMatches(self):
        self.assertEqual(self.arch.worker_entrypoint(), self.arch.worker.entrypoint)

    def testInstantiateWorker(self):
        self.assertTrue(isinstance(self.arch.worker(), DummyWorker))

    def testInstantiateDesigner(self):
        self.assertTrue(isinstance(self.arch.designer(), DummyDesigner))

    def testInstantiateComposer(self):
        self.assertTrue(isinstance(self.arch.composer([ ], [ ]), DummyComposer))


class TestDummyImportedArchitecture(unittest.TestCase):
    '''
        Testcases matching above, but for an architecture that is exposed by an import
    '''
    def setUp(self):
        import dummy_arch as inner_dummy_arch
        self.archPlugins = ArchitecturePlugins([inner_dummy_arch])
        self.arch = self.archPlugins['Dummy']

    def testArchCount(self):
        self.assertEqual(len(self.archPlugins._modules), 1)
        self.assertEqual(len(self.archPlugins.get_architectures()), 1)

    def testGetName(self):
        self.assertEqual(self.arch.get_name(), "Dummy")

    def testGetWorkerEntry(self):
        self.assertTrue(isinstance(self.arch.worker_entrypoint(), Callable))

    def testWorkerEntryMatches(self):
        self.assertEqual(self.arch.worker_entrypoint(), self.arch.worker.entrypoint)

    def testInstantiateWorker(self):
        self.assertTrue(isinstance(self.arch.worker(), DummyWorker))

    def testInstantiateDesigner(self):
        self.assertTrue(isinstance(self.arch.designer(), DummyDesigner))

    def testInstantiateComposer(self):
        self.assertTrue(isinstance(self.arch.composer([ ], [ ]), DummyComposer))


class TestDummyConfigImportedArchitecture(unittest.TestCase):
    '''
        Testcases matching above, but for an architecture loaded
        from a path
    '''
    def setUp(self):
        self.archPlugins = ArchitecturePlugins()
        # Acquire a module and load it into the ArchitecturePlugins
        module = self.archPlugins._load_modules_from_config("./module.conf")[0]
        self.archPlugins._modules.add(module)
        self.archPlugins.load_options_from_modules()
        self.arch = self.archPlugins['Dummy']

    def testArchCount(self):
        self.assertEqual(len(self.archPlugins._modules), 1)
        self.assertEqual(len(self.archPlugins.get_architectures()), 1)

    def testGetName(self):
        self.assertEqual(self.arch.get_name(), "Dummy")

    def testGetWorkerEntry(self):
        self.assertTrue(isinstance(self.arch.worker_entrypoint(), Callable))

    def testWorkerEntryMatches(self):
        self.assertEqual(self.arch.worker_entrypoint(), self.arch.worker.entrypoint)

    def testInstantiateWorker(self):
        self.assertTrue(isinstance(self.arch.worker(), DummyWorker))

    def testInstantiateDesigner(self):
        self.assertTrue(isinstance(self.arch.designer(), DummyDesigner))

    def testInstantiateComposer(self):
        self.assertTrue(isinstance(self.arch.composer([ ], [ ]), DummyComposer))


if __name__ == "__main__":
    unittest.main()

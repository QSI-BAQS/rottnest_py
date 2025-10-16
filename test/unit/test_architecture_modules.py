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


class TestModuleLoading(unittest.TestCase):
    '''
        Testcases related to loading modules (providing architectures)
    '''
    def testModuleFromString(self):
        '''
            @INTERNAL
            Load a module from a string
        '''
        archPlugins = ArchitecturePlugins()
        module = archPlugins._load_module_from_module_string("dummy_arch")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testModuleFromPath(self):
        '''
            @INTERNAL
            Load a module from a path to a Python file that exposes modules
        '''
        archPlugins = ArchitecturePlugins()
        module = archPlugins._load_module_from_file_path("./test_data/standalone.py")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testModuleFromConfigFile(self):
        '''
            @INTERNAL
            Load a module from a path to a config file that declares modules
        '''
        archPlugins = ArchitecturePlugins()
        module = archPlugins._load_modules_from_config("./test_data/module.conf")[0]
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testModuleFromConfigFileArgument(self):
        '''
            Load a module from a config file passed as an argument to the
            architecture plugins
        '''
        archPlugins = ArchitecturePlugins(config_path="./test_data/module.conf")
        self.assertEqual(len(archPlugins), 1)

    def testPluginModuleFromConfigFile(self):
        '''
            Load a module into the architecture plugins from a config file
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_config("./test_data/module.conf")
        self.assertEqual(len(archPlugins), 1)
        self.assertTrue("dummy_arch" in archPlugins.get_module_names())
        self.assertTrue("Dummy" in archPlugins.get_architecture_names())

    def testPluginModuleNoConfigFile(self):
        '''
            Ensure config files that don't exist are flagged
        '''
        archPlugins = ArchitecturePlugins()
        self.assertEqual(archPlugins.load_config("this doesn't exist"), FileNotFoundError)

    def testPluginModuleBadConfigFile(self):
        '''
            Try to use a config file with only malformed entries
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(archPlugins), 0)

    def testPluginModuleKeepGoodConfig(self):
        '''
            Ensure that an invalid config file doesn't invalidate prior modules
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_config("./test_data/module.conf")
        self.assertEqual(len(archPlugins), 1)
        archPlugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(archPlugins), 1)

    def testPluginModuleConfigPartiallyValid(self):
        '''
            Ensure that a config file with a mix of valid and invalid
            entries has the valid entries loaded successfully
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_config("./test_data/mixed_module.conf")
        self.assertEqual(len(archPlugins), 1)

    def testPluginModuleFromString(self):
        '''
            Ensures that modules can be loaded from strings
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_modules_from_strings("dummy_arch")
        self.assertEqual(len(archPlugins), 1)

    def testPluginModuleFileFromString(self):
        '''
            Ensures that the fallback to treating strings as file paths works
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_modules_from_strings("test_data/standalone.py")
        self.assertEqual(len(archPlugins), 1)
        self.assertTrue("test_data/standalone.py" in archPlugins.get_loaded_filepaths())

    def testPluginModuleStringInvalid(self):
        '''
            Ensure an invalid module string is a no-op
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_modules_from_strings("uh oh")
        self.assertEqual(len(archPlugins), 0)

    def testPluginModuleStringPartiallyValid(self):
        '''
            Ensure loading from strings where some are valid will
            successfully load the valid targets
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_modules_from_strings("bad", "dummy_arch")
        self.assertEqual(len(archPlugins), 1)

    def testPluginModuleFileNoTargets(self):
        '''
            Ensures a module file with no valid targets is ignored
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_modules_from_strings("test_data/invalid_standalone.py")
        self.assertEqual(len(archPlugins), 0)

    def testPluginModuleFileTargetNoName(self):
        '''
            Ensures a module file that provides a target without a name does not load it
        '''
        archPlugins = ArchitecturePlugins()
        archPlugins.load_modules_from_strings("test_data/non_arch_obj.py")
        self.assertEqual(len(archPlugins), 0)

    def testPluginModuleFileTargetBadName(self):
        '''
            Ensures a module file that has a target with a non-string name
            reports the invalid name
        '''
        archPlugins = ArchitecturePlugins()
        with self.assertRaises(NotImplementedError):
            archPlugins.load_modules_from_strings("test_data/malformed_name_arch.py")


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
        self.assertEqual(len(self.archPlugins), 1)

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
        module = self.archPlugins._load_module_from_file_path("./test_data/standalone.py")
        self.archPlugins._modules.add(module)
        self.archPlugins.load_options_from_modules()
        self.arch = self.archPlugins['Dummy']

    def testArchCount(self):
        self.assertEqual(len(self.archPlugins._modules), 1)
        self.assertEqual(len(self.archPlugins.get_architectures()), 1)
        self.assertEqual(len(self.archPlugins), 1)

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
        self.assertEqual(len(self.archPlugins), 1)

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
        module = self.archPlugins._load_modules_from_config("./test_data/module.conf")[0]
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

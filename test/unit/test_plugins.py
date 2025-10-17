'''
    Testcases related to the creation, importing and basic use of architectures
'''

import unittest

from typing import Type, Callable

# --[ Rottnest Imports ]---
from rottnest.plugins import executables, architectures
from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker
from rottnest.plugins.architecture_plugins import ArchitecturePlugins
from rottnest.plugins.executable_plugins import ExecutablePlugins

# --[ Testing Utilities ]---
# Used to test architecture imports
from dummy_arch.dummy_arch import DummyWorker, DummyDesigner, DummyComposer


class TestArchitectureLoading(unittest.TestCase):
    '''
        Testcases related to loading modules (providing architectures)
    '''
    def setUp(self):
        self.archPlugins = ArchitecturePlugins()

    def testArchitectureFromString(self):
        '''
            @INTERNAL
            Load a module from a string
        '''
        module = self.archPlugins._load_module_from_module_string("dummy_arch")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testArchitectureFromPath(self):
        '''
            @INTERNAL
            Load a module from a path to a Python file that exposes targets
        '''
        module = self.archPlugins._load_module_from_file_path("./test_data/standalone.py")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testArchitectureFromConfigFile(self):
        '''
            @INTERNAL
            Load a module from a path to a config file that declares modules
        '''
        module = self.archPlugins._load_modules_from_config("./test_data/arch_module.conf")[0]
        self.assertEqual(len(module.rottnest_architectures), 1)

    def testArchitectureFromConfigFileArgument(self):
        '''
            Load a module from a config file passed as an argument to the
            architecture plugins
        '''
        self.archPlugins = ArchitecturePlugins(config_path="./test_data/arch_module.conf")
        self.assertEqual(len(self.archPlugins), 1)

    def testPluginArchitectureFromConfigFile(self):
        '''
            Load a module into the architecture plugins from a config file
        '''
        self.archPlugins.load_config("./test_data/arch_module.conf")
        self.assertEqual(len(self.archPlugins), 1)
        self.assertTrue("dummy_arch" in self.archPlugins.get_module_names())
        self.assertTrue("Dummy" in self.archPlugins.get_architecture_names())

    def testPluginArchitectureNoConfigFile(self):
        '''
            Ensure config files that don't exist are flagged
        '''
        self.assertEqual(self.archPlugins.load_config("this doesn't exist"), FileNotFoundError)

    def testPluginArchitectureBadConfigFile(self):
        '''
            Try to use a config file with only malformed entries
        '''
        self.archPlugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(self.archPlugins), 0)

    def testPluginArchitectureKeepGoodConfig(self):
        '''
            Ensure that an invalid config file doesn't invalidate prior modules
        '''
        self.archPlugins.load_config("./test_data/arch_module.conf")
        self.assertEqual(len(self.archPlugins), 1)
        self.archPlugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(self.archPlugins), 1)

    def testPluginArchitectureConfigPartiallyValid(self):
        '''
            Ensure that a config file with a mix of valid and invalid
            entries has the valid entries loaded successfully
        '''
        self.archPlugins.load_config("./test_data/arch_mixed_validity.conf")
        self.assertEqual(len(self.archPlugins), 1)

    def testPluginArchitectureFromString(self):
        '''
            Ensures that modules can be loaded from strings
        '''
        self.archPlugins.load_modules_from_strings("dummy_arch")
        self.assertEqual(len(self.archPlugins), 1)

    def testPluginArchitectureFileFromString(self):
        '''
            Ensures that the fallback to treating strings as file paths works
        '''
        self.archPlugins.load_modules_from_strings("test_data/standalone.py")
        self.assertEqual(len(self.archPlugins), 1)
        self.assertTrue("test_data/standalone.py" in self.archPlugins.get_loaded_filepaths())

    def testPluginArchitectureStringInvalid(self):
        '''
            Ensure an invalid module string is ignored
        '''
        self.archPlugins.load_modules_from_strings("uh oh")
        self.assertEqual(len(self.archPlugins), 0)

    def testPluginArchitectureStringPartiallyValid(self):
        '''
            Ensure loading from strings where some are valid will
            successfully load the valid targets
        '''
        self.archPlugins.load_modules_from_strings("bad", "dummy_arch")
        self.assertEqual(len(self.archPlugins), 1)

    def testPluginArchitectureFileNoTargets(self):
        '''
            Ensures a module file with no valid targets is ignored
        '''
        self.archPlugins.load_modules_from_strings("test_data/invalid_standalone.py")
        self.assertEqual(len(self.archPlugins), 0)

    def testPluginArchitectureFileTargetNoName(self):
        '''
            Ensures a module file that provides a target without a name does not load it
        '''
        self.archPlugins.load_modules_from_strings("test_data/non_arch_obj.py")
        self.assertEqual(len(self.archPlugins), 0)

    def testPluginArchitectureFileTargetBadName(self):
        '''
            Ensures a module file that has a target with a non-string name
            reports the invalid name
        '''
        with self.assertRaises(NotImplementedError):
            self.archPlugins.load_modules_from_strings("test_data/malformed_name_arch.py")

    def testPluginArchitectureMixedModule(self):
        '''
            Ensures a module that exposes architectures and executables can be loaded
        '''
        self.archPlugins.load_config("test_data/mixed_module.conf")
        self.assertEqual(len(self.archPlugins), 1)

    def testPluginArchitecturePathConfig(self):
        '''
            Ensures a config that provides a path (rather than a module)
            can be loaded
        '''
        self.archPlugins.load_config("test_data/arch_path_module.conf")
        self.assertEqual(len(self.archPlugins), 1)


class TestExecutableLoading(unittest.TestCase):
    '''
        Tests the loading of executables (same underlying system as architectures,
        largely covered by the above testcases)
    '''
    def setUp(self):
        self.exePlugins = ExecutablePlugins()

    def testExecutableFromString(self):
        '''
            @INTERNAL
            Load a module from a string
        '''
        module = self.exePlugins._load_module_from_module_string("dummy_exec")
        self.assertEqual(len(module.rottnest_executables), 1)

    def testExecutableFromPath(self):
        '''
            @INTERNAL
            Load a module from a path to a Python file that exposes targets
        '''
        module = self.exePlugins._load_module_from_file_path("./test_data/standalone.py")
        self.assertEqual(len(module.rottnest_executables), 1)

    def testExecutableFromConfigFile(self):
        '''
            @INTERNAL
            Load a module from a path to a config file that declares modules
        '''
        module = self.exePlugins._load_modules_from_config("./test_data/exec_module.conf")[0]
        self.assertEqual(len(module.rottnest_executables), 1)

    def testExecutableFromConfigFileArgument(self):
        '''
            Load a module from a config file passed as an argument to the
            executable plugins
        '''
        self.exePlugins = ExecutablePlugins(config_path="./test_data/exec_module.conf")
        self.assertEqual(len(self.exePlugins), 1)

    def testPluginExecutableFromConfigFile(self):
        '''
            Load a module into the executable plugins from a config file
        '''
        self.exePlugins.load_config("./test_data/exec_module.conf")
        self.assertEqual(len(self.exePlugins), 1)
        self.assertTrue("dummy_exec" in self.exePlugins.get_module_names())
        self.assertTrue("DummyExecutable" in self.exePlugins.get_executable_names())

    def testPluginExecutableNoConfigFile(self):
        '''
            Ensure config files that don't exist are flagged
        '''
        self.assertEqual(self.exePlugins.load_config("this doesn't exist"), FileNotFoundError)

    def testPluginExecutableBadConfigFile(self):
        '''
            Try to use a config file with only malformed entries
        '''
        self.exePlugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(self.exePlugins), 0)

    def testPluginExecutableFromString(self):
        '''
            Ensures that modules can be loaded from strings
        '''
        self.exePlugins.load_modules_from_strings("dummy_exec")
        self.assertEqual(len(self.exePlugins), 1)

    def testPluginExecutableStringInvalid(self):
        '''
            Ensure an invalid module string is ignored
        '''
        self.exePlugins.load_modules_from_strings("uh oh")
        self.assertEqual(len(self.exePlugins), 0)

    def testPluginExecutableStringPartiallyValid(self):
        '''
            Ensure loading from strings where some are valid will
            successfully load the valid targets
        '''
        self.exePlugins.load_modules_from_strings("bad", "dummy_exec")
        self.assertEqual(len(self.exePlugins), 1)

    def testPluginExecutableFileNoTargets(self):
        '''
            Ensures a module file with no valid targets is ignored
        '''
        self.exePlugins.load_modules_from_strings("test_data/invalid_standalone.py")
        self.assertEqual(len(self.exePlugins), 0)

    def testPluginExecutableMixedModule(self):
        '''
            Ensures a module that exposes executables and architectures can be loaded
        '''
        self.exePlugins.load_config("test_data/mixed_module.conf")
        self.assertEqual(len(self.exePlugins), 1)



class TestDummyArchitecture(unittest.TestCase):
    '''
        Testcases related to the bare minimum inspection of an architecture
        loaded as a plugin
    '''
    def setUp(self):
        self.archPlugins = ArchitecturePlugins()
        self.archPlugins.load_modules_from_strings("dummy_arch")
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

    def testGetSetArch(self):
        self.archPlugins.set_current_architecture("Dummy")
        self.assertTrue(self.archPlugins["Dummy"] is self.archPlugins.get_current_architecture())


if __name__ == "__main__":
    unittest.main()

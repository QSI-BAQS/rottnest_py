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
        self.arch_plugins = ArchitecturePlugins()

    def test_architecture_from_string(self):
        '''
            @INTERNAL
            Load a module from a string
        '''
        module = self.arch_plugins._load_module_from_module_string("dummy_arch")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def test_architecture_from_path(self):
        '''
            @INTERNAL
            Load a module from a path to a Python file that exposes targets
        '''
        module = self.arch_plugins._load_module_from_file_path("./test_data/standalone.py")
        self.assertEqual(len(module.rottnest_architectures), 1)

    def test_architecture_from_config_file(self):
        '''
            @INTERNAL
            Load a module from a path to a config file that declares modules
        '''
        module = self.arch_plugins._load_modules_from_config("./test_data/arch_module.conf")[0]
        self.assertEqual(len(module.rottnest_architectures), 1)

    def test_architecture_from_config_file_argument(self):
        '''
            Load a module from a config file passed as an argument to the
            architecture plugins
        '''
        self.arch_plugins = ArchitecturePlugins(config_path="./test_data/arch_module.conf")
        self.assertEqual(len(self.arch_plugins), 1)

    def test_plugin_architecture_from_config_file(self):
        '''
            Load a module into the architecture plugins from a config file
        '''
        self.arch_plugins.load_config("./test_data/arch_module.conf")
        self.assertEqual(len(self.arch_plugins), 1)
        self.assertTrue("dummy_arch" in self.arch_plugins.get_module_names())
        self.assertTrue("Dummy" in self.arch_plugins.get_architecture_names())

    def test_plugin_architecture_no_config_file(self):
        '''
            Ensure config files that don't exist are flagged
        '''
        self.assertEqual(self.arch_plugins.load_config("this doesn't exist"), FileNotFoundError)

    def test_plugin_architecture_bad_config_file(self):
        '''
            Try to use a config file with only malformed entries
        '''
        self.arch_plugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(self.arch_plugins), 0)

    def test_plugin_architecture_keep_good_config(self):
        '''
            Ensure that an invalid config file doesn't invalidate prior modules
        '''
        self.arch_plugins.load_config("./test_data/arch_module.conf")
        self.assertEqual(len(self.arch_plugins), 1)
        self.arch_plugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(self.arch_plugins), 1)

    def test_plugin_architecture_config_partially_valid(self):
        '''
            Ensure that a config file with a mix of valid and invalid
            entries has the valid entries loaded successfully
        '''
        self.arch_plugins.load_config("./test_data/arch_mixed_validity.conf")
        self.assertEqual(len(self.arch_plugins), 1)

    def test_plugin_architecture_from_string(self):
        '''
            Ensures that modules can be loaded from strings
        '''
        self.arch_plugins.load_modules_from_strings("dummy_arch")
        self.assertEqual(len(self.arch_plugins), 1)

    def test_plugin_architecture_file_from_string(self):
        '''
            Ensures that the fallback to treating strings as file paths works
        '''
        self.arch_plugins.load_modules_from_strings("test_data/standalone.py")
        self.assertEqual(len(self.arch_plugins), 1)
        self.assertTrue("test_data/standalone.py" in self.arch_plugins.get_loaded_filepaths())

    def test_plugin_architecture_string_invalid(self):
        '''
            Ensure an invalid module string is ignored
        '''
        self.arch_plugins.load_modules_from_strings("uh oh")
        self.assertEqual(len(self.arch_plugins), 0)

    def test_plugin_architecture_string_partially_valid(self):
        '''
            Ensure loading from strings where some are valid will
            successfully load the valid targets
        '''
        self.arch_plugins.load_modules_from_strings("bad", "dummy_arch")
        self.assertEqual(len(self.arch_plugins), 1)

    def test_plugin_architecture_file_no_targets(self):
        '''
            Ensures a module file with no valid targets is ignored
        '''
        self.arch_plugins.load_modules_from_strings("test_data/invalid_standalone.py")
        self.assertEqual(len(self.arch_plugins), 0)

    def test_plugin_architecture_file_target_no_name(self):
        '''
            Ensures a module file that provides a target without a name does not load it
        '''
        self.arch_plugins.load_modules_from_strings("test_data/non_arch_obj.py")
        self.assertEqual(len(self.arch_plugins), 0)

    def test_plugin_architecture_file_target_bad_name(self):
        '''
            Ensures a module file that has a target with a non-string name
            reports the invalid name
        '''
        with self.assertRaises(NotImplementedError):
            self.arch_plugins.load_modules_from_strings("test_data/malformed_name_arch.py")

    def test_plugin_architecture_mixed_module(self):
        '''
            Ensures a module that exposes architectures and executables can be loaded
        '''
        self.arch_plugins.load_config("test_data/mixed_module.conf")
        self.assertEqual(len(self.arch_plugins), 1)

    def test_plugin_architecture_path_config(self):
        '''
            Ensures a config that provides a path (rather than a module)
            can be loaded
        '''
        self.arch_plugins.load_config("test_data/arch_path_module.conf")
        self.assertEqual(len(self.arch_plugins), 1)


class TestExecutableLoading(unittest.TestCase):
    '''
        Tests the loading of executables (same underlying system as architectures,
        largely covered by the above testcases)
    '''
    def setUp(self):
        self.exec_plugins = ExecutablePlugins()

    def test_executable_from_string(self):
        '''
            @INTERNAL
            Load a module from a string
        '''
        module = self.exec_plugins._load_module_from_module_string("dummy_exec")
        self.assertEqual(len(module.rottnest_executables), 1)

    def test_executable_from_path(self):
        '''
            @INTERNAL
            Load a module from a path to a Python file that exposes targets
        '''
        module = self.exec_plugins._load_module_from_file_path("./test_data/standalone.py")
        self.assertEqual(len(module.rottnest_executables), 1)

    def test_executable_from_config_file(self):
        '''
            @INTERNAL
            Load a module from a path to a config file that declares modules
        '''
        module = self.exec_plugins._load_modules_from_config("./test_data/exec_module.conf")[0]
        self.assertEqual(len(module.rottnest_executables), 1)

    def test_executable_from_config_file_argument(self):
        '''
            Load a module from a config file passed as an argument to the
            executable plugins
        '''
        self.exec_plugins = ExecutablePlugins(config_path="./test_data/exec_module.conf")
        self.assertEqual(len(self.exec_plugins), 1)

    def test_plugin_executable_from_config_file(self):
        '''
            Load a module into the executable plugins from a config file
        '''
        self.exec_plugins.load_config("./test_data/exec_module.conf")
        self.assertEqual(len(self.exec_plugins), 1)
        self.assertTrue("dummy_exec" in self.exec_plugins.get_module_names())
        self.assertTrue("DummyExecutable" in self.exec_plugins.get_executable_names())

    def test_plugin_executable_no_config_file(self):
        '''
            Ensure config files that don't exist are flagged
        '''
        self.assertEqual(self.exec_plugins.load_config("this doesn't exist"), FileNotFoundError)

    def test_plugin_executable_bad_config_file(self):
        '''
            Try to use a config file with only malformed entries
        '''
        self.exec_plugins.load_config("./test_data/bad_module.conf")
        self.assertEqual(len(self.exec_plugins), 0)

    def test_plugin_executable_from_string(self):
        '''
            Ensures that modules can be loaded from strings
        '''
        self.exec_plugins.load_modules_from_strings("dummy_exec")
        self.assertEqual(len(self.exec_plugins), 1)

    def test_plugin_executable_string_invalid(self):
        '''
            Ensure an invalid module string is ignored
        '''
        self.exec_plugins.load_modules_from_strings("uh oh")
        self.assertEqual(len(self.exec_plugins), 0)

    def test_plugin_executable_string_partially_valid(self):
        '''
            Ensure loading from strings where some are valid will
            successfully load the valid targets
        '''
        self.exec_plugins.load_modules_from_strings("bad", "dummy_exec")
        self.assertEqual(len(self.exec_plugins), 1)

    def test_plugin_executable_file_no_targets(self):
        '''
            Ensures a module file with no valid targets is ignored
        '''
        self.exec_plugins.load_modules_from_strings("test_data/invalid_standalone.py")
        self.assertEqual(len(self.exec_plugins), 0)

    def test_plugin_executable_mixed_module(self):
        '''
            Ensures a module that exposes executables and architectures can be loaded
        '''
        self.exec_plugins.load_config("test_data/mixed_module.conf")
        self.assertEqual(len(self.exec_plugins), 1)



class TestDummyArchitecture(unittest.TestCase):
    '''
        Testcases related to the bare minimum inspection of an architecture
        loaded as a plugin
    '''
    def setUp(self):
        self.arch_plugins = ArchitecturePlugins()
        self.arch_plugins.load_modules_from_strings("dummy_arch")
        self.arch = self.arch_plugins['Dummy']

    def test_arch_count(self):
        self.assertEqual(len(self.arch_plugins._modules), 1)
        self.assertEqual(len(self.arch_plugins.get_architectures()), 1)
        self.assertEqual(len(self.arch_plugins), 1)

    def test_get_name(self):
        self.assertEqual(self.arch.get_name(), "Dummy")

    def test_get_worker_entry(self):
        self.assertTrue(isinstance(self.arch.worker_entrypoint(), Callable))

    def test_worker_entry_matches(self):
        self.assertEqual(self.arch.worker_entrypoint(), self.arch.worker.entrypoint)

    def test_instantiate_worker(self):
        self.assertTrue(isinstance(self.arch.worker(), DummyWorker))

    def test_instantiate_designer(self):
        self.assertTrue(isinstance(self.arch.designer(), DummyDesigner))

    def test_instantiate_composer(self):
        self.assertTrue(isinstance(self.arch.composer([ ], [ ]), DummyComposer))

    def test_get_set_arch(self):
        self.arch_plugins.set_current_architecture("Dummy")
        self.assertTrue(self.arch_plugins["Dummy"] is self.arch_plugins.get_current_architecture())


if __name__ == "__main__":
    unittest.main()

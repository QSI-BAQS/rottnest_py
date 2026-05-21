'''
    Testcases related to loading plugins
'''

import unittest
import sys
import os, os.path

import importlib

from rottnest import config as rottnest_config
# Unbind default config loading
rottnest_config.configuration_locations = []

from rottnest.plugins.architecture_plugins import ArchitecturePlugins
from rottnest.plugins.executable_plugins import ExecutablePlugins

# Set correct working dir (unit directory)
target_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(target_dir)


def mk_plugin_tests(plugin_type, config_test_pairs=dict(), str_test_pairs=dict(), module_test_pairs=dict()):
    '''
        plugin_type: ArchitecturePlugins | ExecutablePlugins

        config_test_pairs:
            tests loading from config (as part of constructor)
            a map test path (str) -> expected outcome
            outcome can be an exception (for failing w/ that exception), an integer (for loading that
            many options successfully), or a set of strings (for loading exactly options with the given names)

        str_test_pairs:
            tests loading from string
            a map str (filepath | module name) -> expected outcome
            outcome is as above

        module_test_pairs:
            tests loading from already-imported module
            a map module -> expected outcome
            outcome is as above
    '''
    class PluginTests(unittest.TestCase):
        def setUp(self):
            self.plugins = plugin_type()
            self.base_plugin_len = len(self.plugins)
            self.base_option_set = set(self.plugins._options.keys())
            self.check_plugin_delta = lambda n: len(self.plugins) == n + self.base_plugin_len


        def test_config_loading(self):
            for target, outcome in config_test_pairs.items():
                with self.subTest(target=target, outcome=outcome):
                    if isinstance(outcome, type) and issubclass(outcome, Exception):
                        self.assertRaises(outcome, lambda *a: plugin_type(config_path=target))
                    elif isinstance(outcome, int):
                        self.plugins = plugin_type(config_path=target)
                        self.assertTrue(self.check_plugin_delta(outcome))
                    else:
                        self.plugins = plugin_type(config_path=target)
                        options_added = set(self.plugins._options.keys()) - self.base_option_set
                        self.assertEqual(outcome, options_added)


        def test_str_loading(self):
            for target, outcome in str_test_pairs.items():
                with self.subTest(target=target, outcome=outcome):
                    # Refresh plugins object
                    self.plugins = plugin_type()
                    if isinstance(outcome, type) and issubclass(outcome, Exception):
                        self.assertRaises(
                            outcome,
                            lambda *a: self.plugins.load_modules_from_strings(target),
                        )
                    elif isinstance(outcome, int):
                        self.plugins.load_modules_from_strings(target)
                        self.assertTrue(self.check_plugin_delta(outcome))
                    else:
                        self.plugins.load_modules_from_strings(target)
                        options_added = set(self.plugins._options.keys()) - self.base_option_set
                        self.assertEqual(outcome, options_added)

        def test_module_loading(self):
            for target, outcome in module_test_pairs.items():
                with self.subTest(target=target, outcome=outcome):
                    # Refresh plugins object
                    self.plugins = plugin_type()
                    if isinstance(outcome, type) and issubclass(outcome, Exception):
                        self.assertRaises(
                            outcome,
                            lambda *a: self.plugins.load_options_from_modules(target),
                        )
                    elif isinstance(outcome, int):
                        self.plugins.load_options_from_modules(target)
                        self.assertTrue(self.check_plugin_delta(outcome))
                    else:
                        self.plugins.load_options_from_modules(target)
                        options_added = set(self.plugins._options.keys()) - self.base_option_set
                        self.assertEqual(outcome, options_added)



    PluginTests.__name__ = f"TestPlugins<{plugin_type.__name__}>"
    PluginTests.__qualname__ = f"TestPlugins<{plugin_type.__name__}>"

    return PluginTests


TestArchPlugins = mk_plugin_tests(ArchitecturePlugins,
    config_test_pairs = {
        # Loads a local module by path
        "./test_configs/arch_valid_path_config": 1,
        # Loads rottnest_preprocessor (NOTE: This is always already loaded, hence no delta,
        # but is also the only module we can guarantee is available to the suite)
        "./test_configs/arch_valid_module_config": 0,
        # Doesn't exist
        "./test_configs/this_path_does_not_exist": FileNotFoundError,
        # Loads the above local module + tries to load something invalid
        "./test_configs/arch_partially_valid_config": {"TestLoadingArchitecture"},
        # Contains architecture and executable
        "./test_configs/mixed_path_config": {"TestLoadingArchitecture"},
        # Contains only executables
        "./test_configs/exec_valid_path_config": 0,
        # Contains an architecture w/ no name
        "./test_configs/arch_bad_module_config": 0,
        # Contains an empty module
        "./test_configs/empty_module_config": 0,
    },
    str_test_pairs = {
        "test_configs/test_loading_architecture.py": {"TestLoadingArchitecture"},
        "test_configs/this_path_does_not_exist": FileNotFoundError,
        "test_configs/test_loading_arch_no_name.py": 0,
        "test_configs/test_loading_executable.py": 0,
        "rottnest_preprocessor": 0
    },
    module_test_pairs = {
        # TODO
    },
)


TestExecPlugins = mk_plugin_tests(ExecutablePlugins,
    config_test_pairs = {
        # Loads a local module by path
        "./test_configs/exec_valid_path_config": 1,
        # Doesn't exist
        "./test_configs/this_path_does_not_exist": FileNotFoundError,
        # Loads the above local module + tries to load something invalid
        "./test_configs/exec_partially_valid_config": {"TestLoadingExecutable"},
        # Contains architecture and executable
        "./test_configs/mixed_path_config": {"TestLoadingExecutable"},
        # Contains only architectures
        "./test_configs/arch_valid_path_config": 0,
        # Contains an empty module
        "./test_configs/empty_module_config": 0,
    },
    str_test_pairs = {
        "test_configs/test_loading_executable.py": {"TestLoadingExecutable"},
        "test_configs/this_path_does_not_exist": FileNotFoundError,
        "test_configs/test_loading_arch_no_name.py": 0,
        "test_configs/test_loading_architecture.py": 0,
        "rottnest_preprocessor": 0
    },
    module_test_pairs = {
        # TODO
    },
)


if __name__ == "__main__":
    unittest.main()

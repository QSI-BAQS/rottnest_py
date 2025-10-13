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

from utils.arch_factory import build_arch, build_worker, build_designer, build_composer


class TestDummyImportedArchitecture(unittest.TestCase):
    '''
        Testcases related to the bare minimum inspection of an architecture
        loaded as a plugin
        (ensure that getters and attributes expose the correct things)
    '''
    def setUp(self):
        self.archPlugins = ArchitecturePlugins(None, None)
        self.archPlugins.load_modules_from_strings("dummy_arch")
        self.arch = self.archPlugins['Dummy']

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

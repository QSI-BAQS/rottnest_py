'''
    Tests end to end execution
'''
import unittest
import math

import cirq

# These workers have been tested without the pool elsewhere
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest_preprocessor.preprocessor.architecture import PreprocessorArchitecture

from rottnest.test_utils.executable import sample_executable 

from rottnest.process_pool import standalone

from rottnest.plugins import architectures, executables
from rottnest.test_utils.plugin_setup import setup_plugins_decorator 


layout_id = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(layout_id, layout)

class ProcessPoolTests(unittest.TestCase):

    @setup_plugins_decorator()
    def test_standalone(self):
        '''
            Tests non-pool execution
        '''
        executable = executables.get_current_option()
        architecture = architectures.get_current_option()
        result = standalone.compile(
            LayoutProxy.get_layouts(),
            executable,
            architecture,
            compile_from_graph=False 
        )



if __name__ == '__main__':
    obj = ProcessPoolTests()
    obj.test_standalone()

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

from rottnest.plugins import architectures


layout_id = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(layout_id, layout)

class ProcessPoolTests(unittest.TestCase):

    def test_standalone(self):
        '''
            Tests non-pool execution
        '''
        executable = sample_executable()
        architecture = PreprocessorArchitecture 

        # Saves architecture for preprocessor
        prev_arch = architectures.get_current_architecture()
        architectures._force_set_current_architecture(PreprocessorArchitecture)

        result = standalone.compile(
            layout_id,
            executable(),
            architecture,
            compile_from_graph=False 
        )

        architectures._force_set_current_architecture(prev_arch)


if __name__ == '__main__':
    obj = ProcessPoolTests()
    obj.test_standalone()

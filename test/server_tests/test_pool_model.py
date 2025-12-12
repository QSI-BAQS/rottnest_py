'''
    Tests model calls for the process pool
'''

import unittest
from rottnest.server.model import process_pool 
from rottnest.server.model import executable 

from rottnest.test_utils.executable import sample_executable, sample_executable_with_params, n_rz_gates
from rottnest.test_utils.plugin_support import add_executable, add_architecture

from rottnest.server.model import architecture as architecture_model, executable as executable_model

from rottnest.compute_units.layout_proxy import LayoutProxy
from rottnest.preprocessor.architecture import PreprocessorArchitecture


class PoolModelTests(unittest.TestCase):
    '''
        Test operation of the pool via the model
    '''

    def test_standalone_cirq(self, n_qubits=100, depth=10):
        '''
            Test model calls for standalone 
             compilation on a cirq circuit 
        '''
        # Setup and hook executable and architecture to plugin singletons
        executable = sample_executable(n_qubits=n_qubits, depth=depth) 
        architecture = PreprocessorArchitecture 

        add_executable(None, executable)
        add_architecture(None, PreprocessorArchitecture)

        # Create the pool object
        pool = process_pool.ModelProcessPool()

        architecture_model.set_current_architecture(None)
        executable_model.set_current_executable(None)

        result = pool.execute_standalone(compile_from_graph=False)
        assert result.get_n_rz() ==  n_rz_gates(n_qubits=n_qubits, depth=depth)

    def test_standalone_cirq_params(self, n_qubits=50, depth=5):
        '''
            Test model calls for standalone 
             compilation on a cirq circuit 
        '''
        # Setup and hook executable and architecture to plugin singletons
        executable = sample_executable_with_params() 
        architecture = PreprocessorArchitecture 

        add_executable(None, executable)
        add_architecture(None, PreprocessorArchitecture)

        # Create the pool object
        pool = process_pool.ModelProcessPool()

        architecture_model.set_current_architecture(None)
        executable_model.set_current_executable(None)
        executable_model.set_current_params(
            {
                'n_qubits': 50,
                'depth': 5
            }
        )

        result = pool.execute_standalone(compile_from_graph=False)
        assert result.get_n_rz() ==  n_rz_gates(n_qubits=n_qubits, depth=depth)


if __name__ == '__main__':
    obj =  PoolModelTests()
    obj.test_standalone_cirq_params()

'''
    Tests end to end execution
'''
import unittest
import math

import cirq

# These workers have been tested without the pool elsewhere
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.preprocessor.architecture import PreprocessorArchitecture

from utils.executable import CirqExecutable

from rottnest.process_pool import standalone

from rottnest.plugins import architectures


layout_id = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(layout_id, layout)

class ProcessPoolTests(unittest.TestCase):

    def generate_cirq_toffoli(self, ctrl_0, ctrl_1, targ):
        t_rot = math.pi / 4
        t_dag_rot = -1 * t_rot

        circ = cirq.Circuit(
            cirq.H(ctrl_0),
            cirq.CNOT(ctrl_1, ctrl_0),
            cirq.Rz(rads=t_dag_rot)(ctrl_0),
            cirq.CNOT(targ, ctrl_0),
            cirq.Rz(rads=t_rot)(ctrl_0),
            cirq.CNOT(targ, ctrl_0),
            cirq.Rz(rads=t_dag_rot)(ctrl_0),
            cirq.CNOT(ctrl_1, ctrl_0),
            cirq.Rz(rads=t_rot)(ctrl_0),
            cirq.Rz(rads=t_rot)(targ),
            cirq.CNOT(ctrl_1, targ),
            cirq.Rz(rads=t_rot)(ctrl_1),
            cirq.Rz(rads=t_dag_rot)(targ),
            cirq.CNOT(ctrl_1, targ),
            cirq.H(ctrl_0)
        )
        return circ 

    def generate_cirq_circuit(self, n_qubits: int, depth: int):
        '''
            Generates simple helper circuits
        '''
        circ = cirq.Circuit()
        cirq_qubits = tuple(cirq.NamedQubit(str(x)) for x in range(n_qubits))

        for _ in range(depth):
            for i, j, k in zip(range(n_qubits), range(1, n_qubits), range(2, n_qubits)): 
                circ.append(
                    self.generate_cirq_toffoli(
                        cirq_qubits[i],
                        cirq_qubits[j],
                        cirq_qubits[k]
                    )
                )
        return circ

    def n_rz_gates(self, n_qubits: int = 100, depth: int = 10):
        '''
            Simple counter for the number of rz gates
            in the toffoli sequence
        '''
        return (n_qubits - 2) * depth * 7


    def generate_executable(self, n_qubits = 100, depth=10):
        '''
            Wrapper to create a rottnest executable object
        '''
        circ = self.generate_cirq_circuit(n_qubits, depth)
        return CirqExecutable(circ)
    

    def test_standalone(self):
        '''
            Tests non-pool execution
        '''
        executable = self.generate_executable()
        architecture = PreprocessorArchitecture 

        # Saves architecture for preprocessor
        prev_arch = architectures.get_current_architecture()
        architectures._force_set_current_architecture(PreprocessorArchitecture)

        result = standalone.compile(
            layout_id,
            executable,
            architecture,
            compile_from_graph=False 
        )

        architectures._force_set_current_architecture(prev_arch)

    def test_process_pool(self):
        '''
            Tests executing the process pool with an Rz counter architecture 
        '''
        return
        pool = ComputeUnitExecutorPool() 
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()
        
        from t_scheduler.region_builder.json_to_region import json_to_layout, example as layout 
        from rottnest.compute_units.layout_proxy import LayoutProxy

        LayoutProxy.add_layout(layout)

        pool.synchronise()

        pool.set_architecture_module(
            'Four Stage Superconducting'
        )
        pool.set_executable(
            'Fermi-Hubbard'
        )

        pool.set_executable_params({'N':2, 'pandora':False})

        pool.start_workers()
        import time
        time.sleep(5) 
        pool.run_sequence([0])

        pool.shutdown()

if __name__ == '__main__':
    obj = ProcessPoolTests()
    obj.test_standalone()

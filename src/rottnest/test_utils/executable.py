'''
    Helper objects for testing
'''
import cirq
import math
from rottnest.executables.executable import RottnestExecutable

def generate_cirq_toffoli(ctrl_0, ctrl_1, targ):
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

def generate_cirq_circuit(n_qubits: int, depth: int):
    '''
        Generates simple helper circuits
    '''
    circ = cirq.Circuit()
    cirq_qubits = tuple(cirq.NamedQubit(str(x)) for x in range(n_qubits))

    for _ in range(depth):
        for i, j, k in zip(range(n_qubits), range(1, n_qubits), range(2, n_qubits)): 
            circ.append(
                generate_cirq_toffoli(
                    cirq_qubits[i],
                    cirq_qubits[j],
                    cirq_qubits[k]
                )
            )
    return circ

def n_rz_gates(n_qubits: int = 100, depth: int = 10):
    '''
        Simple counter for the number of rz gates
        in the toffoli sequence
    '''
    return (n_qubits - 2) * depth * 7


def sample_executable(n_qubits = 100, depth=10):
    '''
        Wrapper to create a rottnest executable object
    '''
    circ = generate_cirq_circuit(n_qubits, depth)

    class CirqExecutable(RottnestExecutable):
        '''
            Sample wrapper on cirq objects
            Performs no caching, used for testing only
        '''
        _cirq_obj = circ

        def __init__(self, prec=10):
            self._prec = prec

        @staticmethod
        def get_parameters():
            '''
                No parameters
            '''
            return {}

        def _generate_circuit(self):
            '''
                Getter for the cirq_obj
            '''
            return self._cirq_obj

        def prec_rz(self):
            '''
                Precision doesn't really matter here
            '''
            return self._prec 

    return CirqExecutable



def sample_executable_with_params():
    '''
        Wrapper to create a rottnest executable object
    '''
    class CirqExecutable(RottnestExecutable):
        '''
            Sample wrapper on cirq objects
            Performs no caching, used for testing only
        '''
        _cirq_obj = None  
        _prec = 10

        @staticmethod
        def get_parameters():
            return {
                'n_qubits': (int, 50),
                'depth': (int, 5)
            }

        def _generate_circuit(self):
            '''
                Getter for the cirq_obj
            '''
            if self._cirq_obj is None:
                self._cirq_obj = generate_cirq_circuit(
                    self.n_qubits,
                    self.depth
                )
            return self._cirq_obj

        def prec_rz(self):
            '''
                Precision doesn't really matter here
            '''
            return self._prec 

    return CirqExecutable


class SampleExecutable(RottnestExecutable):
        '''
            Sample wrapper on cirq objects
            Performs no caching, used for testing only
        '''
        _cirq_obj = None  
        _prec = 10

        @staticmethod
        def get_name():
            '''
                Getter for class name
            '''
            return 'Sample Executable'

        @staticmethod
        def get_parameters():
            return {
                'n_qubits': (int, 50),
                'depth': (int, 5)
            }

        def _generate_circuit(self):
            '''
                Getter for the cirq_obj
            '''
            if self._cirq_obj is None:
                self._cirq_obj = generate_cirq_circuit(
                    self.n_qubits,
                    self.depth
                )
            return self._cirq_obj

        def prec_rz(self):
            '''
                Precision doesn't really matter here
            '''
            return self._prec 

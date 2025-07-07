import abc
import cirq

from rottnest.gridsynth.angle_to_rational import angle_to_rational
from rottnest.gridsynth.gridsynth import gs_instance 

class RottnestExecutable(abc.ABC):
    '''
        Interface for Rottnest Executable objects 
    '''

    _prec_rz = None

    def precompute(self, *args, **kwargs):
        '''
            Precomputation of elements of
            the circuit 
        '''
        pass

    def  __call__(self, *args, **kwargs): 
        '''
            Dispatch for circuit generation 
        '''
        return self._generate_circuit(*args, **kwargs)

    def _generate_circuit(self):
        '''
           Abstract circuit generation method
        '''

    def get_parameters(self):
        '''
            Abstract method for returning tunable parameters  
        '''

    def precision_rz(self) -> int:
        '''
            Precision of Rz gates in bits
        '''
        if self._prec_rz is None:
            n_rz = self.n_rz()
            self._prec_rz = int(np.ceil(-1 * np.log2(self.target_prec_rz() / n_rz)))
        return self._prec_rz

    def n_rz(self) -> int:
        '''
            Number of Rz gates
        '''

    def n_T(self):
        '''
            Dipatch method for T counting
        '''


    @staticmethod
    def count_t_cirq(qc: cirq.Circuit, precision: int = None) -> int:
        '''
            Naive T counting
            :: qc : cirq.Circuit :: Cirq circuit to perform T counting over 
            :: precision : int :: Precision in bits for Rz rotations
        '''

        if precision is None:
            precision = self.precision_rz() 

        t_count = 0
        for sl in qc:
            for gate in sl:
                if type(gate.gate) is cirq.ops.common_gates.Rz:
                    angle = gate.gate._rads
                    p, q = angle_to_rational(angle, precision=precision)
                    sequence = gs_instance.z_theta_instruction(p, q, precision=precision)
                    for i in sequence:
                        if i == 'T':
                            t_count += 1
        return t_count

    @staticmethod
    def count_rz_cirq(qc, precision: int = None):
        '''
        Counts the number of rz gates in a cirq circuit
        :: qc : cirq.Circuit :: Cirq circuit to perform Rz counting over
        :: precision: int :: (Optional) Number of bits to truncate the precision 
        Excludes Rz gates that correpond to angles 
        
        Typically it may be worth running this count a few times   
        '''
        rz_count = 0
        T_rotation = 0.25

        if precision is None: 
            eps = 0
        else:
            eps = 2 ** - precision

        for s in qc:
            for gate in s:
                # Can do exact matching on these values as they are powers of two
                # Should really replace this with a bound by delta
                if (
                        (type(gate.gate) is cirq.ops.common_gates.Rz) 
                        and 
                        (gate.gate._rads % T_rotation > eps) # Not within epsilon
                   ):
                    rz_count += 1
        return rz_count

import abc
import cirq
import numpy as np

from functools import reduce

from rottnest.rz_decomposer.angle_to_rational import angle_to_rational
from rottnest.rz_decomposer.gridsynth import Gridsynth 
from rottnest.rz_decomposer.rz_decomposer import DEFAULT_PRECISION 

ROTTNEST_EXECUTABLE_MODULE_TAG = "rottnest_executables"

class RottnestExecutable(abc.ABC):
    '''
        Interface for Rottnest Executable objects 
    '''

    RZ_PREC = 'prec_rz'
    base_params = {RZ_PREC: (int, DEFAULT_PRECISION)}

    # FEATURE: RzDecomposition
    # Move this to a module that can be shared with workers 
    _rz_decomposer = Gridsynth()

    def __init__(self, pandora=False, prec_rz=None, **kwargs):
        '''
        Default constructor for RottnestExecutables
        Loads all parameters from all child classes and sets them to their default value
        :: pandora : bool :: Enables or disables pandora caching 
        '''
        self.pandora = pandora

        if prec_rz is None:
             prec_rz = DEFAULT_PRECISION
        self.prec_rz = prec_rz

        params = (
            self.__class__.get_private_parameters()
            | self.__class__.get_parameters()
        )
        
        for param_name in params:
            param_type, param_value = params[param_name]
            
            if param_name in kwargs:
                param_value = kwargs[param_name]

            # Bind the parameters by name to the class instance
            self.__setattr__(param_name, param_type(param_value))

    @staticmethod
    def get_name():
        '''
            Used to load names to the front end  
        '''
        raise NotImplementedError

    def precompute(self, *args, **kwargs):
        '''
            Precomputation of elements 
            of the circuit
        '''
        pass

    def get_rz_precision(self):
        '''
        '''
        return self.prec_rz

    def  __call__(self, *args, **kwargs): 
        '''
            Dispatch for circuit generation 
        '''
        return self._generate_circuit(*args, **kwargs)

    def _generate_circuit(self):
        '''
           Abstract circuit generation method
        '''
        raise NotImplementedError

    @classmethod
    def get_parameters(cls):
        '''
        Class dispatch method to recursively collect parameters and default arguments 
        To set parameters for a given executable the default behaviour is to use the
        _parameters method
        Parameter priority is in order of a BFS over the bases of each object in the 
        inheritence hierachy 
        '''
        params = {}
        # Collect parameters from subclasses
        for base in cls.__bases__:
            print(base, base.get_parameters())
            if issubclass(base, RottnestExecutable) and base is not object:
                # Recurse
                params |= base.get_parameters() 

        # Set this classes params last
        params |= cls._parameters()
        return params


    @classmethod
    def get_private_parameters(cls):
        '''
        Class dispatch method to recursively collect private parameters and default arguments 
        To set parameters for a given executable the default behaviour is to use the
        _parameters method
        Parameter priority is in order of a BFS over the bases of each object in the 
        inheritence hierachy 
        '''
        params = {}
        # Collect parameters from subclasses
        for base in cls.__bases__:
            if issubclass(base, RottnestExecutable) and base is not RottnestExecutable:
                # Recurse
                params |= base.get_private_parameters() 

        # Set this classes params last
        params |= cls._private_parameters()
        return params

    @staticmethod
    def _parameters():
        '''
            Abstract method for returning tunable parameters 
            This is invoked through the class dispatch method get_parameters
            The default behaviour for the dispatch method is to aggregate parameters
            through inherited classes
            { <name> : (type, None),
              <name> : (type, default_value)}
        '''

    @staticmethod
    def _private_parameters():
        '''
            Abstract method for returning tunable parameters 
            Private parameters are not exposed to the 
            front end
            
            These parameters bind in the constructor
            and are typically used for internal methods
            without needing to rewrite __init__
            unless more complex logic is needed 

            { <name> : (type, None),
              <name> : (type, default_value)}
        '''
        return {}

    def n_rz(self) -> int:
        '''
            Number of Rz gates
        '''

    def bound_rz(self) -> int:
        '''
            Upper bounds the number of Rz gates
        '''
        return self.n_rz()

    def precision_rz(self) -> int:
        '''
            Baseline precision of Rz gates in bits
            Certain circuits may need to override this
            on either a per-gate or global scope
        '''
        if self._prec_rz is None:
            n_rz = self.bound_rz()
            self._prec_rz = int(np.ceil(-1 * np.log2(self.target_prec_rz() / n_rz)))
        return self._prec_rz

    def magic_states_supported(self) -> str:
        '''
            What magic states this circuit requires
            Default to 'T', as CCZ can be decomposed
        '''
        return ('T')

    def bound_T(self):
        '''
            Upper bounds the number of T gates
        '''
        return self.n_T()

    def n_MSF(self):
        '''
            Dipatch method for magic state counting
        '''

    def count_t_cirq(self, qc: cirq.Circuit, precision: int = None) -> int:
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
                    sequence = self._rz_decomposer.z_theta_instruction(p, q, precision=precision)
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
                # Bound by delta of a T rotation
                # T gates are caught elsewhere 
                if (
                        (type(gate.gate) is cirq.ops.common_gates.Rz) 
                        and 
                        (gate.gate._rads % T_rotation > eps) # Not within epsilon
                   ):
                    rz_count += 1
        return rz_count

    def get_qubits(self):
        '''
            Top level getter for qubits
            Override this as appropriate to skip computation of the circuit   
        '''
        return self._generate_circuit().all_qubits()
  
    def _get_qubits_from_pyliqtr_object(self):
        '''
            Helper method for pyliqtr iterable objects
        '''

    def _get_qubits_from_qualtran_object(self):
        '''
            Helper method for pyliqtr iterable objects
        '''

    def _get_qubits_from_cirq_object(self):
        '''
            Helper method for pyliqtr iterable objects
        '''
 
    def _get_qubits_from_list_of_gates(self):
        '''
            Helper method for non-circ iterables
            Composes qubits via union of sets 
        '''
        qubits = set()
        for gate in self._generate_circuit():
            if not isinstance(gate, list):
                qubits |= set(gate.qubits)
            else:
                for g in gate:
                    qubits |= set(g.qubits)
        return qubits

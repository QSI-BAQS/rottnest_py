import abc
import cirq
import numpy as np

from typing import Iterable

# from functools import reduce

from rottnest.rz_decomposer.angle_to_rational import angle_to_rational
from rottnest.rz_decomposer.rz_decomposer import DEFAULT_PRECISION 

ROTTNEST_EXECUTABLE_MODULE_TAG = "rottnest_executables"

class RottnestExecutable(abc.ABC):
    '''
        Interface for Rottnest Executable objects 
    '''

    NO_ANALYTICAL_METHOD = object()

    RZ_PREC = 'prec_rz'
    base_params = {}


    def __init__(self, pandora=True, prec_rz=None, **kwargs):
        '''
        Default constructor for RottnestExecutables
        Loads all parameters from all child classes and sets them to their default value
        :: pandora : bool :: Enables or disables pandora caching 
        '''
        self._pandora = pandora

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

    def precompute(self, *args, **kwargs) -> Iterable:
        '''
            Dynamic dispatch of precomputation of circuit
             elements. 
            This dispatch method also handles pandora 
             switching logic
            Defers to _precompute for inheritance  
        '''
        if not self._pandora:
            return dict() 
        return self._precompute()

    def _precompute(self) -> Iterable:
        '''
            Generates an iterable of hashes and pre
             computation objects to pass to Pandora   
        '''
        return dict()


    def get_rz_counts(self) -> object | dict:
        '''
Method to get the rz precision
If it returns NO_ANALYTICAL_METHOD then this will default 
 to an Rz counter in the preprocessing pass
Otherwise returns a dict of keys as angles and integers
 as counts 
        '''
        return self.NO_ANALYTICAL_METHOD

    def get_t_fidelity(self) -> object | float:
        '''
Method to get the magic state fidelity
If this method returns NO_ANALYTICAL_METHOD then it will
default to a counter in the preprocessing pass 
        '''
        return self.NO_ANALYTICAL_METHOD


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
            # print(base, base.get_parameters())
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

    @classmethod
    def pyliqtr_patchers(self) -> dict():
        '''
            Any custom pyliqtr hashes needed for this executable
        '''
        return dict()

    @classmethod
    def qualtran_patchers(self) -> dict():
        '''
            Any custom qualtran hashes needed for this executable

        '''
        return dict()

    @classmethod
    def cirq_patchers(self) -> dict():
        '''
            Any custom cirq hashes needed for this executable
        '''
        return dict()

    @classmethod
    def cirq_gate_decomposers(self) -> dict():
        '''
            Any custom cirq to cabaliser decomposers needed
        '''
        return dict()


    def n_rz(self) -> int:
        '''
            Number of Rz gates
        '''
        raise NotImplementedError('Currently not implemented: '
                                  + self.n_rz.__name__)
        return 0

    def bound_rz(self) -> int:
        '''
            Upper bounds the number of Rz gates
        '''
        return self.n_rz()

    def target_prec_rz(self):
        '''
            NOTE: This is being called but it is unknown
                what this should be 
            TODO: This method should probably be
                completed and it looks like it is wanting
                a count
        '''
        raise NotImplementedError('Not currently implemented: '
                                  + self.target_prec_rz.__name__)
        return 0

    def precision_rz(self) -> int:
        '''
            Baseline precision of Rz gates in bits
            Certain circuits may need to override this
            on either a per-gate or global scope
        '''
        if self._prec_rz is None:
            n_rz = self.bound_rz()
            self._prec_rz = int(np.ceil(-1 * np.log2( \
                self.target_prec_rz() / n_rz)))
        return self._prec_rz

    def magic_states_supported(self) -> str:
        '''
            What magic states this circuit requires
            Default to 'T', as CCZ can be decomposed
        '''
        return ('T')

    def n_T(self) -> int:
        '''
            NOTE: This is being called but it is unknown
                what this should be 
            TODO: This method should probably be
                completed and it looks like it is wanting
                a count
        '''
        raise NotImplementedError('Not currently implemented: '
                                  + self.n_T.__name__)
        return 0

    def bound_T(self):
        '''
            Upper bounds the number of T gates
        '''
        return self.n_T()

    def n_MSF(self):
        '''
            Dipatch method for magic state counting
        '''

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



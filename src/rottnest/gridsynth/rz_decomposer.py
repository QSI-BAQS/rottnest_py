import abc
from typing import Iterable

class RzDecomposer(abc.ABC):

    def set_precision(self, precision: int):
        '''
            Sets the minimum precision of the decomposer
        '''
    
    def z_theta_instruction(self, p, q, *, precision=None, **kwargs) -> Iterable:
        '''
            Decompose Rz(p / q, 2 ** -precision) to a sequence of H, T, S  
        '''

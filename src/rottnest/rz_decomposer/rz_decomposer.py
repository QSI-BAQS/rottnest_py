import abc
from typing import Iterable

from rottnest.gridsynth.gridsynth import DEFAULT_PRECISION

class RzDecomposer(abc.ABC):

    def set_precision(self, precision: int):
        '''
            Sets the minimum precision of the decomposer
        '''

    def get_precision(self) -> int:
        '''
            Gets the current precision
        '''
    
    def z_theta_instruction(self, p, q, *, precision=None, **kwargs) -> Iterable:
        '''
            Decompose Rz(p / q, 2 ** -precision) to a sequence of H, T, S  
        '''

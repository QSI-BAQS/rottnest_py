import abc
from typing import Iterable

DEFAULT_PRECISION = 10 

class RzDecomposer(abc.ABC):

    @abc.abstractmethod
    def set_rz_precision(self, precision: int):
        '''
            Sets the minimum precision of the decomposer
        '''
    @abc.abstractmethod
    def get_rz_precision(self) -> int:
        '''
            Gets the current precision
        '''
    @abc.abstractmethod
    def z_theta_instruction(self, p, q, *, precision=None, **kwargs) -> Iterable:
        '''
            Decompose Rz(p / q, 2 ** -precision) to a sequence of H, T, S  
        '''

import abc
from typing import Iterable

DEFAULT_PRECISION = 10 

class RzDecomposer(abc.ABC):
    '''
        Abstract base class for a decomposer
    '''
    INSTANTIATED = False
    def __init__(self):

        '''
            Hard check against multiple instantiation
        '''
        self.singleton_validation()

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

    @classmethod
    def singleton_validation(cls):
        assert cls.INSTANTIATED is False
        cls.INSTANTIATED = True

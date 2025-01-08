import abc
import typing

from cabaliser.operation_sequence import OperationSequence

class OperationTagFactory(abc.ABC): 
    '''
        Operation tag factory method
        Abstracts tag generators
    '''

    @abstractmethod
    def __iter__(self) -> typing.Iterable:
        '''
            Iterates over the factory, generating tagged objects
        '''
        ...


class OperationTag(abc.ABC):
    '''
    Callable object that regenerates and returns a deterministic sequence of operations 
    '''

    @abstractmethod
    def _generate(self) -> typing.Iterable:
        '''
    Callable and re-callable method for 
    construcing an operation sequence
    This should abstract away the call location
        '''
        pass

    def __iter__(self) -> typing.Iterable:
        '''
        Iterator for passing the operation sequence
        '''
        for i in self._generate():  
            yield i

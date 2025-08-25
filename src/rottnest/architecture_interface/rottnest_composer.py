'''
    Rottnest Composer interface

    This class handles program logic relating 
    to the composition of widgets

'''
import abc
from typing import Type
from types import GeneratorType

class RottnestComposer(abc.ABC):
    '''
        Handles composition of compilation units 
    '''

    @staticmethod
    def results_composer() -> Type["ResultsComposer"]:
        return ResultsComposer 


class ResultsComposer:
    '''
        Composition object for composing results
        Technically only requires:
        __add__   :: Composition under addition 
        __iadd__  :: In place addition
        serialise :: Maps to a front-end readable form 

        This is a default implementation and should be 
         overwritten by the architecture module
        
        This assumption assumes that the backing is a
        dictionary of objects where values composer under
         addition 
    '''

    def __init__(self, result_obj: dict):
        '''
            Constructor
        '''
        self._obj = result_obj 
    
    def __iadd__(self, other):
        for key, val in other.items():
            res._obj[key] = res._obj.get(key, 0) + val 

    def __add__(self, other):
        res = ResultsComposer(**self._obj)
        for key, val in other.items():
            res._obj[key] = res._obj.get(key, 0) + val 
        return res

    def serialise(self):
        '''
            Returns a representation for display on the 
              front end
        '''
        return str(self._obj)

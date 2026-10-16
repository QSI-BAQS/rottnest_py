from collections.abc import Callable
from typing import Any


class RottnestParameterType:
    '''
       To support some more specialised types that are described differently
       between Python and JS type systems 
    '''
    def __init__(self, name: str, convert: Callable[[Any], Any]):
        '''
            Initialises a parameter type, overrides the __name__
        '''
        self.__name__ = name
        self.conversion = convert

    def __call__(self, val):
        '''
           Have to override this method to ensure it calls the object method 
        '''
        return self.conversion(val)


class RottnestParameter:
    '''
       RottnestParameter - These are the specialised types
       which will need to be annotated appropriately 
    '''
    BigInt = RottnestParameterType('BigInt', lambda x: int(x))
    BigDecimal = RottnestParameterType('BigDecimal', lambda x: float(x))
    CodeString = RottnestParameterType('CodeString', lambda x: x)

    @classmethod
    def get_parameter_map(cls):
        '''
           Constructs a paramter map 
        '''
        param_map = {}
        for k in cls.__dict__:
            obj = cls.__dict__[k]
            if isinstance(obj, RottnestParameterType):
                param_map[k] = obj        
        return param_map

    @classmethod
    def get_parameter(cls, typename: str):
        '''
           Attempts to get the parameter that is registered
           as a special paramter 
        '''
        typemap = cls.get_parameter_map()
        param = None
        if typename in typemap:
            param = typemap[typename]

        return param
        

    @classmethod
    def is_special_type(cls, typename: str):
        '''
           Checks if the typename is a special type that is listed here
        '''
        typemap = cls.get_parameter_map()
        obj = typemap[typename]
        return obj is not None


class RottnestParameterType:
    '''
       To support some more specialised types that are described differently
       between Python and JS type systems 
    '''
    def __init__(self, name: str):
        '''
            Initialises a parameter type, overrides the __name__
        '''
        self.__name__ = name


class RottnestParameter:
    '''
       RottnestParameter - These are the specialised types
       which will need to be annotated appropriately 
    '''
    BigInt = RottnestParameterType('BigInt')
    BigDecimal = RottnestParameterType('BigDecimal')

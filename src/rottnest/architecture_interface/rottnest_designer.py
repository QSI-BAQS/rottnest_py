'''
    Rottnest Designer interface

    This class handles program logic relating 
    to designing implementations of architectures 

'''
import abc
from functools import reduce

class RottnestDesigner(abc.ABC):
    '''
        RottnestDesigner, the designer_metadata will need to
        ensure you have designer metadata that is usable for the frontend 
    '''

    DESIGNER_SYMBOLS  = "DESIGNER_SYMBOLS "
    VISUALISER_SYMBOLS = "VISUALISER_SYMBOLS"
    RUNCHART_SYMBOLS = "RUNCHART_SYMBOLS"

    @staticmethod
    def get_mem_bound(architecture_template: dict):
        '''
            Calculates the memory bound per widget for
            an architecture
        '''
        raise NotImplementedError

    @staticmethod
    def get_T_rate(architecture_template: dict):
        '''
            Calculates an approximate T state generation rate
            Currently unused
        '''
        raise NotImplementedError

    @staticmethod
    def get_designer_metadata():
        '''
           Gets the designer metadata for the frontend that will
           outline the position of the frontend files to be loaded
        '''
        raise NotImplementedError

    @staticmethod
    def get_designer_data():
        '''
           Gets the designer data for the backend that will
           outline functions that will be callable by when
           messages map to the websocket protocol
        '''
        raise NotImplementedError

    @classmethod
    def get_designer_strings(cls) -> dict:
        '''
            Gets the collection of fields for front-end descriptions,
            names and types with associated back-end bindings
        '''
        return reduce(
            lambda a, b: a | b,
            (
                self.get_designer_symbols(),
                self.get_visualiser_symbols(),
                self.get_runchart_symbols(),
            )
        )

    @staticmethod
    def get_designer_symbols() -> dict:
        '''
            Symbols for the designer
            Symbols should be a dictionary of string keys to 
             FrontEndSymbol objects
        '''
        return {}

    @staticmethod
    def get_visualiser_symbols() -> dict:
        '''
            Symbols for the visualiser
            Symbols should be a dictionary of string keys to 
             FrontEndSymbol objects
        '''
        return {}

    @staticmethod
    def get_runchart_symbols() -> dict:
        '''
            Symbols for the runchart
            Symbols should be a dictionary of string keys to 
             FrontEndSymbol objects
        '''
        return {}

class FrontEndSymbol:
    '''
        Symbol interface for the front end
        Exposed in nested collections by get designer strings
    '''
    def __init__(
            self,
            symbol: str,
            name: str, 
            symbol_type: type,
            description: str):
        '''
            Constructor
        '''
        self._symbol = symbol
        self._name = name
        self._symbol_type = symbol_type
        self._description = description

    def to_dict(self):
        '''
            Serialisation function
        '''
        return {self._symbol: (self._name, self._symbol_type, self._description)}


    def to_serializable_dict(self):
        '''
           This is to ensure that the type can be serialized 
        '''

        return {self._symbol: (self._name, self._symbol_type.__name__, self._description)}

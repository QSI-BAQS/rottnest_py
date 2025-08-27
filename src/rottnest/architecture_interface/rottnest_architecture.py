'''
    Rottnest Architecture descriptor
    All architecture plugins should expose an object of this type 
'''
import abc
from types import FunctionType
from typing import Type

ROTTNEST_ARCHITECTURE_MODULE_TAG = 'rottnest_architectures'

class RottnestArchitecture(abc.ABC):
    '''
        Rottnest architecture interface
        Legal architectures should implement the methods in this interface 
        In most cases methods will actually be static references to class constructors
        
        These methods are themselves a collection of derived interfaces - the types specified
        are all themselves abstract types  
    '''

    @staticmethod
    def get_name(self) -> str:
        '''
            Gets the name of the architecture object
            This will be used as a key for a selector
        '''
        raise NotImplementedError

    @classmethod
    def worker_entrypoint(cls, *args, **kwargs) -> FunctionType:
        '''
        Returns an entrypoint function for a worker  
        Workers are worker pool members that injest 
        widgets and emit serialisable objects that 
        composers may ingest  
        '''
        return cls.worker.entrypoint 

    @staticmethod
    def worker(*args, **kwargs) -> Type["RottnestWorker"]:
        '''
        Optional for testing
        Returns a RottnestWorker object
        '''
        pass

    @staticmethod
    def composer(*args, **kwargs) -> Type["RottnestComposer"]: 
        '''
            Gets a composer type
            Composers define logic to combine the outputs of workers 
        '''
        raise NotImplementedError

    @staticmethod
    def designer(*args, **kwargs) -> Type["RottnestDesigner"]:
        '''
            Generates any hooks needed for indicating what front-end designer is required 
        '''
        raise NotImplementedError


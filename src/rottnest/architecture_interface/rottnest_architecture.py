'''
    Rottnest Architecture descriptor
    All architecture plugins should expose an object of this type 
'''
import abc

from rottnest.process_pool import process_worker

class RottnestArchitecture(abc.ABC):
    '''
        Rottnest architecture interface
        Legal architectures should implement the methods in this interface 
        In most cases methods will actually be static references to class constructors
        
        These methods are themselves a collection of derived interfaces - the types specified
        are all themselves abstract types  
    '''
    @staticmethod
    def worker_entrypoint(*args, **kwargs) -> fn:
        '''
        Returns an entrypoint function for a worker  
        Workers are worker pool members that injest 
        widgets and emit serialisable objects that 
        composers may ingest  
        '''    

    @staticmethod
    def composer(*args, **kwargs) -> RottnestComposer: 
        '''
            Gets a composer type
            Composers define logic to combine the outputs of workers 
        '''

    @staticmethod
    def designer(*args, **kwargs):  
        '''
            Generates any hooks needed for indicating what front-end designer is required   
        '''

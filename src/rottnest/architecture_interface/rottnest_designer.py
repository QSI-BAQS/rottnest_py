'''
    Rottnest Designer interface

    This class handles program logic relating 
    to designing implementations of architectures 

'''
import abc

class RottnestDesigner(abc.ABC):
    '''
        RottnestDesigner, the designer_metadata will need to
        ensure you have designer metadata that is usable for the frontend 
    '''

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

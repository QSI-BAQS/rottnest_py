'''
    Rottnest Designer interface

    This class handles program logic relating 
    to designing implementations of architectures 

'''
import abc

class RottnestDesigner(abc.ABC):
    '''
        
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

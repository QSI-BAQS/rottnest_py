'''
    Singleton for the Rz decomposer
    Useful as a source of truth
'''

from . import gridsynth

class RzDecomposerSingleton:

    # Currently defaults to Gridsynth
    __RZ_DECOMPOSER = None 

    @classmethod
    def get_rz_decomposer(cls):
        '''
            Getter for the singleton instance
        '''
        if cls.__RZ_DECOMPOSER is None:
            cls.__RZ_DECOMPOSER = gridsynth.Gridsynth()
        return cls.__RZ_DECOMPOSER

    @classmethod
    def set_rz_decomposer(cls, composer):
        '''
            Setter for the singleton instance
        '''
        cls.__RZ_DECOMPOSER = composer

    @classmethod
    def get_rz_precision(cls):
        '''
            Simple getter for the precision, without loading the decomposer outside of the context
        '''
        return get_rz_decomposer().get_rz_precision()

    @classmethod
    def set_rz_precision(cls, precision):
        '''
        '''
        decomp = get_rz_decomposer()
        decomp.set_rz_precision(precision)


def get_rz_decomposer():
    '''
        Getter for the singleton instance
    '''
    return RzDecomposerSingleton.get_rz_decomposer()

def set_rz_decomposer(composer):
    '''
        Setter for the singleton instance
    '''
    return RzDecomposerSingleton.set_rz_decomposer(composer)


def get_rz_precision():
    '''
        Simple getter for the precision, without loading the decomposer outside of the context
    '''
    return RzDecomposerSingleton.get_rz_precision()


def set_rz_precision(precision):
    return RzDecomposerSingleton.set_rz_precision(precision)


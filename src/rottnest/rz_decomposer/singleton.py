'''
    Singleton for the Rz decomposer
    Useful as a source of truth
'''

from . import gridsynth

# Currently defaults to Gridsynth
__RZ_DECOMPOSER = None 


def get_rz_decomposer():
    '''
        Getter for the singleton instance
    '''
    if __RZ_DECOMPOSER is None:
        __RZ_DECOMPOSER = gridsynth.Gridsynth()
    return __RZ_DECOMPOSER

def set_rz_decomposer(composer):
    '''
        Setter for the singleton instance
    '''
    __RZ_DECOMPOSER = composer

def get_rz_precision():
    '''
        Simple getter for the precision, without loading the decomposer outside of the context
    '''
    return get_rz_decomposer().get_precision()

def set_rz_precision(precision):
    '''
    '''
    decomp = get_rz_decomposer()
    decomp.set_precision(precision)

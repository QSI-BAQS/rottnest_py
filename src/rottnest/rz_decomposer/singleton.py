'''
    Singleton for the Rz decomposer
    Useful as a source of truth
'''

from . import gridsynth

# Currently defaults to Gridsynth
__RZ_DECOMPOSER = gridsynth.Gridsynth()


def get_rz_decomposer():
    '''
        Getter for the singleton instance
    '''
    return __RZ_DECOMPOSER

def set_rz_decomposer(composer):
    '''
        Setter for the singleton instance
    '''
    __RZ_DECOMPOSER = composer

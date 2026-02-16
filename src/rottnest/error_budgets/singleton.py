'''
    Singleton instance of the error budget
    # TODO: Link to the plugin system
'''
from .even_distribution import EvenDistribution

error_budget_object = EvenDistribution()

def get_error_budget():
    '''
        Getter for the singleton instance
    '''
    return error_budget_object

def set_p_physical(p_phys):
    '''
    Dipatch to singleton setter
    '''
    error_budget_object.set_p_physical(p_phys)

def set_target_error(err: float):
    '''
    Dispatch to singleton setter
    '''
    error_budget_object.set_target_error(err)

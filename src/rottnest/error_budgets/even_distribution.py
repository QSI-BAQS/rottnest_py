'''
    Even distribution error model
'''
from .error_budget import ErrorBudget


class EvenDistribution(ErrorBudget):
    '''
        Simple even error distribution model
    '''

    def __init__(self, 
        p_physical=1e-3,
        target_error = 1e-2
    ):
        '''
            Constructor for an even distribution
        '''
        super().__init__(p_physical, target_error)

    def get_rz_precision_budget(self) -> float:
        '''
            Sets an even split
        '''
        return self.get_target_error() / 4

    def get_t_fidelity_budget(self) -> float:
        '''
            Sets an even split
        '''
        return self.get_target_error() / 4
               
    def get_space_time_budget(self) -> float:
        '''
            Sets an even split
        '''
        return self.get_target_error() / 4

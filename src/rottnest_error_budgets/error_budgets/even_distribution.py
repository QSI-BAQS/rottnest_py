'''
    Even distribution error model
'''
from rottnest.error_budgets.error_budget import ErrorBudget


class EvenDistribution(ErrorBudget):
    '''
        Simple even error distribution model
    '''

    MODEL_NAME = "Bounded Sum"
    DEFAULT_COEFF = 4

    def __init__(
                self,
                target_error: float = 1e-2,
                coeff: float = None
            ):
        '''
            Constructor for an even distribution
        '''
        if coeff is None:
            coeff = self.DEFAULT_COEFF
        assert coeff >= 3

        self.coeff = coeff

        super().__init__(target_error)

    @classmethod
    def get_name(cls):
        '''
            Getter
        '''
        return cls.MODEL_NAME

    @classmethod
    def get_parameters(cls):
        '''
            Getter for model parameters
        '''
        return (
            cls.get_base_model_parameters()
            | {
                'coeff': (float, cls.DEFAULT_COEFF)
              }
        )

    def get_rz_precision_budget(self) -> float:
        '''
            Sets an even split
        '''
        return self.get_target_error() / self.coeff

    def get_t_infidelity_budget(self) -> float:
        '''
            Sets an even split
        '''
        return self.get_target_error() / self.coeff

    def get_topological_error_budget(self) -> float:
        '''
            Sets an even split
        '''
        return self.get_target_error() / self.coeff

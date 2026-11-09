'''
    Error Budget base class and interface
'''
import abc


class ErrorBudget(abc.ABC):
    '''
        Error budget base class
    '''

    def __init__(
                self,
                target_error: float
            ):
        '''
            Error budget base class
        '''
        # Global target error rate across all sources
        self._target_error = target_error

    @classmethod
    def get_model_name(cls):
        '''
            Getter for a model name to expose to an API
        '''

    @classmethod
    def get_base_model_parameters(cls):
        '''
            Simple getter for some base parameters
        '''
        return {
            'target_error': (float, 0.3)
        }

    @classmethod
    def get_model_parameters(cls):
        '''
            Getter for model parameters
        '''

    def get_target_error(self) -> float:
        '''
            Gets the target error
        '''
        return self._target_error

    def set_target_error(self, target_error):
        '''
            Setter for the target error rate
        '''
        self._target_error = target_error

    def validate(self, rz_err=None, t_err=None, topological_errors=None):
        '''
            Validates that all errors are less than
            budget targets
        '''
        # TODO - decide a nice implementation

    @abc.abstractmethod
    def get_rz_precision_budget(self) -> float:
        '''
            Base Rz precision budget getter
        '''

    @abc.abstractmethod
    def get_topological_error_budget(self) -> float:
        '''
        Base topological budget getter
        '''

    @abc.abstractmethod
    def get_t_infidelity_budget(self) -> float:
        '''
            Base T infidelity budget getter
        '''


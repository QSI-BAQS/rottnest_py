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
            p_physical: float,
            target_error: float
        ):
        '''
            Error budget base class
        '''

        self._p_physical = p_physical
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
            'p_physical': (float, None),
            'target_error': (float, None)
        }

    @classmethod
    def get_model_parameters(cls):
        '''
            Getter for model parameters
        '''

    def get_p_physical(self) -> float:
        '''
            Get the physical error rate
        '''
        return self._p_physical

    def set_p_physical(self, p_physical):
        '''
            Setter for the physical error rate
        '''
        self._p_physical = p_physical

    def get_target_error(self) -> float:
        '''
            Gets the target erro
        '''
        return self._target_error

    def set_target_error(self, target_error):
        '''
            Setter for the target error rate
        '''
        self._target_error = target_error

    def validate(self, rz_err=None, t_err=None, stv_err=None):
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
    def get_t_infidelity_budget(self) -> float:
        '''
            Base T infidelity budget getter
        '''

    @abc.abstractmethod
    def get_space_time_budget(self) -> float:
        '''
        Base space-time budget getter
        '''

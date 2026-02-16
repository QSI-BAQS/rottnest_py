from abc
'''
    Error Budget base class and interface
'''


class ErrorBudget(abc.ABC):
    '''
        Error budget base class
    '''

    def __init__(
            self,
            p_physical: float,
            target_err: float
        ): 
        '''
            Error budget base class
        '''

        self._p_physical = p_physical
        self._target_error = target_error

    def get_p_physical(self) -> float:
        '''
            Get the physical error rate
        '''
        return self.p_physical
  
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

    @abc.abstractclassmethod
    def validate(self, **errs):
        '''
            Validates that all errors are less than
            budget targets
        '''
 
    @abc.abstractclassmethod
    def get_rz_precision_budget(self) -> float:
        ...

    @abc.abstractclassmethod
    def get_t_fidelity_budget(self) -> float:
        ...
               
    @abc.abstractclassmethod
    def get_space_time_budget(self) -> float:
        ...


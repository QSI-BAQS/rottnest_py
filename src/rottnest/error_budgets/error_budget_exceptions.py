'''
    Exceptions for error budget classes
'''


class ErrorBudgetUnsatisifiableException(Exception):
    '''
        Unsatisfiable error budget
        Typically caused by bad parameters 
        :: err_msg : str :: Override field on error string
    '''

    MSG = "Error Budget Constraints Unsatisfiable"
    def __init__(self, *args, err_msg: str = None, **kwargs):
        '''
            Dispatch constructor  
        '''
        if err_msg is None:
            # Use default
            err_msg = self.MSG

        super().__init__(err_msg, *args, **kwargs)

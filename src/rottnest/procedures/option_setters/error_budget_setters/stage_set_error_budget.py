'''
    Simple setter for the error budget
    TODO: Extend this with the plugin system for different budget setters
'''

from rottnest.procedures import stage
from rottnest.error_budgets import set_target_error, set_p_physical 

STAGE_TAG = 'set_error_budget'

class SetErrorBudgetStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, target_error=None, p_phys=None):
        '''
            Constructor
        '''
        self._target_error = target_error 
        self._p_phys = p_phys

        self._complete = False
        if dependencies is None:
            dependencies = [] 
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Synchronises and starts the workers
        '''

        if self._target_error is not None:
            set_target_error(self._target_error) 

        if self._p_phys is not None:
            set_p_physical(self._p_phys) 


        self._complete = True

'''
    Stage for calculating the T fidelity required
'''
import numpy as np

from rottnest.plugins import architectures, executables
from rottnest.procedures import stage

from rottnest.error_budgets import get_error_budget

from . import stage_t_count


STAGE_TAG = 'get_t_infidelity'

class TFidelityStage(stage.RottnestCompilerStage):
    '''
        Calculates the fidelity of the T states 
    '''
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False
        self._t_infidelity = None

        if dependencies is None:
            dependencies = [
                stage_t_count.STAGE_TAG
            ] 

        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, environment):
        '''
           Calculates the T fidelity 
           Technically this uses the infidelity
        '''
        # TODO: Load from external
        budget = get_error_budget()
        err_budget = budget.get_t_infidelity_budget() 

        t_count = environment.get_t_count()
        if t_count == 0:
            t_count += 1
        self._t_infidelity = err_budget / t_count
        self._complete = True

    def __call__(self):
        '''
            Dispatches to get_rz_count
        '''
        return self.get_t_infidelity()

    def get_t_infidelity(self):
        '''
            Getter for the t fidelity
        '''
        return self._t_infidelity

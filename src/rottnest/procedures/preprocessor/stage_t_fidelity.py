'''
    Stage for calculating the T fidelity required
'''
import numpy as np

from rottnest.plugins import architectures, executables
from rottnest.procedures import stage

from rottnest.rz_decomposer import get_rz_decomposer
from rottnest.rz_decomposer.angle_to_rational import trivial_angle_filters_float, angle_to_rational

from . import stage_t_count


STAGE_TAG = 'get_t_fidelity'

class TFidelityStage(stage.RottnestCompilerStage):
    '''
        Calculates the fidelity of the T states 
    '''
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False
        self._t_fidelity = None

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
        '''
        # TODO: Load from external
        err_budget = 1e-4
        t_count = environment.get_t_count()
        self._t_fidelity = err_budget / t_count
        self._complete = True

    def __call__(self):
        '''
            Dispatches to get_rz_count
        '''
        return self.get_t_fidelity()

    def get_t_fidelity(self):
        '''
            Getter for the t fidelity
        '''
        return self._t_fidelity

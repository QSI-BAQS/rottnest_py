'''
    Stage for hotswapping architectures
'''
import numpy as np

from rottnest.plugins import architectures, executables
from rottnest.procedures import stage

from rottnest.rz_decomposer import get_rz_decomposer
from rottnest.error_budgets import get_error_budget

from . import stage_rz_count 


STAGE_TAG = 'set_rz_precision'

class RzPrecisionStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False
        self._prec_rz = None

        if dependencies is None:
            dependencies = [
                stage_rz_count.STAGE_TAG
            ] 

        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, environment):
        '''
            Sets the number of bits of precision needed for the Rz decomposer
        '''
       
        # Gets the total number of rz gates
        rz_counts = environment.get_rz_count()  

        # Error budget for rz
        budget = get_error_budget()
        err = budget.get_rz_precision_budget() 
        if rz_counts == 0: 
            print("No Rz gates found")
            self._prec_rz = 1
       
        else: 
            self._prec_rz = int(
                np.ceil(
                    np.log2(
                        rz_counts / err
                    )
                )
            )

        # Get the decomposer
        decomposer = get_rz_decomposer() 
        decomposer.set_rz_precision(self._prec_rz)
 
        self._complete = True

    def get_rz_precision(self):
        '''
            Getter for the rz precision
        '''
        return self._prec_rz
    
    def __call__(self):
        '''
            Dispatch to getter
        '''
        return self.get_rz_precision()

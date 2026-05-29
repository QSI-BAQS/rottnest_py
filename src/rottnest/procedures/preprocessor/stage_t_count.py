'''
    Stage for hotswapping architectures
'''
from decimal import Decimal

from rottnest.plugins import architectures, executables
from rottnest.procedures import stage

from rottnest.rz_decomposer import get_rz_decomposer
from rottnest.rz_decomposer.angle_to_rational import trivial_angle_filters_float, angle_to_rational

from . import stage_set_rz_precision


STAGE_TAG = 'get_t_count'

class TCountStage(stage.RottnestCompilerStage):
    '''
        Stage for counting T gates
        Depends on Rz evaluation
    '''
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        self._complete = False
        self._t_count = None

        if dependencies is None:
            dependencies = [
                stage_set_rz_precision.STAGE_TAG
            ] 

        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, environment):
        '''
            Resets a swapped architecture back to an
            original one            
        '''
        # Get the composer
        rz_counts = environment.pool_procedure.get_results()

        # Get the precision in bits
        decomposer = get_rz_decomposer() 
        precision_bits = decomposer.get_rz_precision()

        # Precision as a float
        precision = 2 ** (-1 * precision_bits)
        # Count the T states in the table
        t_count = 0
        for angle, count in rz_counts.items():

            # Convert the angle 
            numerator, denominator = angle_to_rational(angle, precision=precision_bits)

            # Construct the sequence
            seq = decomposer.z_theta_instruction(numerator, denominator, precision=precision_bits)
            
            # Count T gates
            t_count += count * sum(
                (1 for i in seq if i == 'T')
            )

        self._t_count = t_count
        self._complete = True

    def __call__(self):
        '''
            Dispatches to get_rz_count
        '''
        return self.get_t_count()

    def get_t_count(self):
        '''
            Getter for the rz count
        '''
        return self._t_count

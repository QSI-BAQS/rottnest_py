from rottnest.procedures import pool, procedure

from . import stage_set_preproc_architecture
from . import stage_reset_preproc_architecture
from . import stage_set_preproc_layout
from . import stage_reset_preproc_layout
from . import stage_rz_count
from . import stage_set_rz_precision
from . import stage_t_count
from . import stage_t_fidelity

from rottnest.compute_units.layout_proxy import LayoutProxy

STAGE_TAG = 'preprocessor_procedure'

class PreprocessorProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):


        # TODO: Replace this with dynamic loads
        
        swap_arch = stage_set_preproc_architecture.SetPreprocessingArchitectureStage()

        swap_layout = stage_set_preproc_layout.SetPreprocessingLayoutStage(
            dependencies = [swap_arch.get_tag()]
        )

        # Doesn't report to websocket 
        preprocessing_pool = pool.procedure_pool.PoolProcedure(
            reporting = False,
            dependencies = [swap_layout.get_tag()],
            asynchronous = True
        )
        reset_arch = stage_reset_preproc_architecture.ResetPreprocessingArchitectureStage(
            dependencies = [preprocessing_pool.get_tag()]
        )

        reset_layout = stage_reset_preproc_layout.ResetPreprocessingLayoutStage(
            dependencies = [reset_arch.get_tag()]
        )

        rz_count = stage_rz_count.RzCountStage(
            dependencies = [reset_layout.get_tag()]
        )

        rz_precision = stage_set_rz_precision.RzPrecisionStage(
            dependencies = [rz_count.get_tag()]
        )

        t_count = stage_t_count.TCountStage(
            dependencies = [rz_precision.get_tag()]
        )
        t_fidelity = stage_t_fidelity.TFidelityStage(
                    dependencies = [t_count.get_tag()]
        )


        stages = [
            swap_arch,
            swap_layout,
            preprocessing_pool,
            reset_arch,
            reset_layout,
            rz_count,
            rz_precision,
            t_count,
            t_fidelity
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

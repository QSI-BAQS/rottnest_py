from rottnest.procedures import pool, procedure

from . import stage_set_preproc_architecture
from . import stage_reset_preproc_architecture
from . import stage_rz_count
from . import stage_set_rz_precision
from . import stage_t_count


from rottnest.compute_units.layout_proxy import LayoutProxy

STAGE_TAG = 'preprocessor_procedure'

class PreprocessorProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):


        # TODO: Replace this with dynamic loads

        layout_id = 0
        memory_bound = 1000
        layout = {'mem_bound': memory_bound}
        LayoutProxy.add_layout_with_id(layout_id, layout)
   
        
        swap_arch = stage_set_preproc_architecture.SetPreprocessingArchitectureStage()
 
        preprocessing_pool = pool.procedure_pool.PoolProcedure(
            dependencies = [swap_arch.get_tag()],
            asynchronous = True
        )
        reset_arch = stage_reset_preproc_architecture.ResetPreprocessingArchitectureStage(
            dependencies = [preprocessing_pool.get_tag()]
        )

        rz_count = stage_rz_count.RzCountStage(
            dependencies = [reset_arch.get_tag()]
        )

        rz_precision = stage_set_rz_precision.RzPrecisionStage(
            dependencies = [rz_count.get_tag()]
        )

        t_count = stage_t_count.TCountStage(
            dependencies = [rz_precision.get_tag()]
        )

        stages = [
            swap_arch,
            preprocessing_pool,
            reset_arch,
            rz_count,
            rz_precision,
            t_count
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

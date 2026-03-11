from rottnest.procedures import pool, procedure, preprocessor


STAGE_TAG = 'preprocess_and_execute'

class PreprocessorProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):



   
        
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
        t_fidelity = stage_t_fidelity.TFidelityStage(
                    dependencies = [t_count.get_tag()]
        )


        stages = [
            swap_arch,
            preprocessing_pool,
            reset_arch,
            rz_count,
            rz_precision,
            t_count,
            t_fidelity
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

from rottnest.procedures import decomposition_patchers
from rottnest.procedures import pool, procedure 


STAGE_TAG = 'pool_procedure'

class PoolProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, reporting=True, tag=None, dependencies=None, asynchronous=True):

        # Patch the parser
        # This needs to be reflected by the pool manager 
        patchers = decomposition_patchers.DecompositionPatchProcedure()

        manager = pool.stage_start_pool_manager.StartPoolManagerStage(
            dependencies=[patchers.get_tag()] 
        )
        reset_context = pool.stage_reset_context.ResetContextStage(
            dependencies = [manager.get_tag()]
        )

        clear_buffers_initial = pool.stage_clear_buffers.ClearPoolBuffersStage(
            dependencies = [manager.get_tag()],
            tag = "Clear Buffers Before Job"
        )
        synch = pool.stage_synchronise.SynchronisePoolStage(
            dependencies = [clear_buffers_initial.get_tag()]
        )
        workers = pool.stage_start_pool.StartPoolStage(
            dependencies = [synch.get_tag()] 
        )
        run = pool.stage_run_pool.RunPoolStage(
            reporting=reporting,
            dependencies = [workers.get_tag()] 
        )

        results = pool.stage_get_results.GetResultsPoolStage(
           dependencies = [run.get_tag()]
        )


        shutdown = pool.stage_shutdown_pool.ShutdownPoolStage(
            dependencies = [results.get_tag()]
        )

        clear_buffers_final = pool.stage_clear_buffers.ClearPoolBuffersStage(
            dependencies = [shutdown.get_tag()],
            tag = "Clear Buffers to Finalise"
        )

        stages = [
            patchers,
            manager,
            reset_context,
            clear_buffers_initial,
            synch,
            workers,
            run,
            results,
            shutdown,
            clear_buffers_final
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies, asynchronous=asynchronous)


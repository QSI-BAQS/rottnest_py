from rottnest.procedures import pool, procedure 


STAGE_TAG = 'pool_procedure'

class PoolProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, asynchronous=True):

        # TODO:
        # This depends on layout proxy
        manager = pool.stage_start_pool_manager.StartPoolManagerStage()
        synch = pool.stage_synchronise.SynchronisePoolStage(
            dependencies = [manager.get_tag()]
        )
        workers = pool.stage_start_pool.StartPoolStage(
            dependencies = [synch.get_tag()] 
        )
        run = pool.stage_run_pool.RunPoolStage(
            dependencies = [workers.get_tag()] 
        )

        results = pool.stage_get_results.GetResultsPoolStage(
           dependencies = [run.get_tag()]
        )

        shutdown = pool.stage_shutdown_pool.ShutdownPoolStage(
            dependencies = [results.get_tag()]
        )
        stages = [
            manager,
            synch,
            workers,
            run,
            results,
            shutdown
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies, asynchronous=asynchronous)


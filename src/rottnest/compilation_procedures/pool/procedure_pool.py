from rottnest.compilation_procedures import pool, procedure 

class PoolProcedure(procedure.RottnestCompilerProcedure): 

    def __init__(self, *, tag=None, dependencies=None):

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
        shutdown = pool.stage_shutdown_pool.ShutdownPoolStage(
            dependencies = [run.get_tag()]
        )
        stages = [
            manager,
            synch,
            workers,
            run,
            shutdown
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)


from rottnest.compilation_procedures import pool, procedure 

class PoolProcedure(procedure.RottnestCompilerProcedure): 

    def __init__(self, *, tag=None, dependencies=None):
        stages = [
            pool.stage_start_pool_manager.StartPoolManagerStage(),
            pool.stage_start_pool.StartPoolStage(),
            pool.stage_run_pool.RunPoolStage(),
            pool.stage_shutdown_pool.ShutdownPoolStage()
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies) 


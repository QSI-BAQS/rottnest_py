from rottnest.procedures import pool, procedure, preprocessor
from rottnest.debug.util import with_debug_log

STAGE_TAG = 'preprocess_and_execute'

class PreprocAndExecuteProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):

        self._complete = False
        preproc = preprocessor.PreprocessorProcedure(
            asynchronous = True
        )

        execute = pool.PoolProcedure(
            dependencies = [preproc.get_tag()],
            asynchronous = True
        )
        
        stages = [
            preproc,
            execute    
        ]

        super().__init__(
            None,
            stages=stages,
            tag=tag,
            dependencies=dependencies
        )

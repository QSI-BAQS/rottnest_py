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
        self.stage_ref = stages # NOTE: I am not sure if this is wise...

        super().__init__(
            None,
            stages=stages,
            tag=tag,
            dependencies=dependencies
        )

    # @with_debug_log()
    # def poll(self, compiler_environment=None):
    #     '''
    #         Polls the data from its sub-procedures
    #     '''
    #     for s in self.stage_ref:
    #         s.poll()
        

    # @with_debug_log()
    # def complete(self):
    #     '''
    #        Checks to see if the final stage is complete 
    #     '''
    #     if len(self.stage_ref) == 0:
    #         return True
    #     return self.stage_ref[-1].complete()
        

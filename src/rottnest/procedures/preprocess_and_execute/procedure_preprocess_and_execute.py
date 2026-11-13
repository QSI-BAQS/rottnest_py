from rottnest.procedures import pool, procedure, preprocessor

STAGE_TAG = 'preprocess_and_execute'

class PreprocAndExecuteProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, reporting=True, tag=None, dependencies=None):

        self._complete = False
        preproc = preprocessor.PreprocessorProcedure(
            asynchronous = True
        )

        execute = pool.PoolProcedure(
            dependencies = [preproc.get_tag()],
            asynchronous = True,
            reporting=reporting,
            postprocess=True
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

       
    def get_results(self): 
        '''
            Helper function
        '''
        if self.complete():
            return self.pool_procedure.get_results()
        raise Exception("Procedure cannot emit results before it is compleete")

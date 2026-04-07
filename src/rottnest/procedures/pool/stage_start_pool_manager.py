from rottnest.procedures import stage
from rottnest.process_pool.singleton import get_pool

STAGE_TAG = 'Start Pool Manager'

class StartPoolManagerStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None):
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )


    def execute(self, compiler_environment):
        '''
            Starts the pool manager task
        '''
        pool = get_pool()
        pool.start()

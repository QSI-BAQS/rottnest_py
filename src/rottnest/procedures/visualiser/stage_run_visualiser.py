'''
    Runs the visualiser    
'''

from rottnest.process_pool import get_pool

STAGE_TAG = 'run_visualiser'

class RunVisualiserStage(stage.RottnestCompilerStage):
    TAG = STAGE_TAG

    def __init__(self,
                graph_id,
                *,
                reporting=True,
                tag=None,
                dependencies=None,
            ):
        '''
            Constructor
        '''

        self.graph_id = graph_id
        self._reporting = reporting
        self._result = None

        self._complete = False
        if dependencies is None:
            dependencies = [] 
    
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=True
        )

    def execute(self, compiler_environment):
        '''
           Executes the compute unit 
        '''
        pool = get_pool() 
        pool.get_visualiser(self.graph_id)

    def poll(self):
        pool = get_pool()
        obj = pool.get_visualiser_status()
        if obj is not None:
            self._complete = True

            # Reports over the websocket
            if self._reporting:
                app_instance = RottnestApplication.try_get_instance()
                if app_instance is not None:
                    app_instance.websocket_result_write(obj)
            else:
                self.result = obj  

    def complete(self):
        return self._complete

    def get_result(self):
        '''
            Getter function for the result
        '''
        return self.result

    def __call__(self):
        '''
            Wrapper for result getter
        '''
        return self.get_result()

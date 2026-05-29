'''
    Runs the visualiser    
'''
from rottnest.procedures import stage
from rottnest.process_pool import get_pool
from rottnest.procedures.procedure_manager import MPSCChannelProvider
from rottnest.procedures.procedure_manager.mpsc_common import MPSC_VISUALISER_CHANNEL_TAG


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
        self.vis_status_data = None
        self._complete = False
        self._writer = None


        if self._reporting:
            mpsc_instance = MPSCChannelProvider.get_instance()
            mpsc_writer, _mpscstate = mpsc_instance.get_writer(MPSC_VISUALISER_CHANNEL_TAG)
            self._writer = mpsc_writer

        
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

    def poll(self, compiler_environment=None):
        pool = get_pool()
        obj = pool.get_visualiser_status()
        if obj is not None:
            self._complete = True
            if self._reporting:
                self.vis_status_data = obj
                self.result = obj
                if self._writer:
                    self._writer.write(obj)
                                  

    def complete(self):
        '''
            Returns a complete state  
        '''
        return self._complete

    def get_result(self):
        '''
            Getter function for the result
        '''
        return self.result

    def get_vis_status_data(self):
        '''
           Get the visualiser status data 
        '''

    def __call__(self):
        '''
            Wrapper for result getter
        '''
        return self.get_result()

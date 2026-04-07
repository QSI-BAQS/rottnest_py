from rottnest.procedures import stage
from rottnest.monkey_patchers import get_tracking_targets
from rottnest.input_parsers import update_tracking_targets 

STAGE_TAG = 'Parser Tracking'

class ParserTrackingStage(stage.RottnestCompilerStage):
    '''
        Loads hash functions from the executable
        and patches them into the decomposer 
    '''
    TAG = STAGE_TAG 

    def __init__(self, *, tag=None, dependencies=None):
        super().__init__(tag=tag, dependencies=dependencies)

    def execute(self, environment):
        '''
            Extracks the tracking targets and 
            attaches them to the parser
        '''
        tracking_targets = get_tracking_targets() 
        update_tracking_targets(tracking_targets)

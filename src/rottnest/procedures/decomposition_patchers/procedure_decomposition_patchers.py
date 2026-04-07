from rottnest.procedures import procedure

from . import stage_decomposition_patchers
from . import stage_parser_tracking 
STAGE_TAG = 'patchers'

class DecompositionPatchProcedure(procedure.RottnestCompilerProcedure): 
    '''
        Handles patching functions with appropriate
        hashes and decompositions
    '''

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, asynchronous=False):

        patchers = stage_decomposition_patchers.DecomposerPatchStage()

        parser_tracking = stage_parser_tracking.ParserTrackingStage(
            dependencies = [patchers.get_tag()] 
        ) 
        stages = [
            patchers,
            parser_tracking
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies, asynchronous=asynchronous)

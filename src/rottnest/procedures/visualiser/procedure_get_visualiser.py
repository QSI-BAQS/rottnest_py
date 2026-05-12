from rottnest.procedures import procedure

from .stage_run_visualiser import RunVisualiserStage 

STAGE_TAG = 'run_visualiser'

class GetVisualiserProcedure(procedure.RottnestCompilerProcedure): 
    '''
        This procedure triggers a run of the procedure
        on the priority process
    '''
    TAG = STAGE_TAG

    def __init__(
            self,
            graph_id,
            *,
            reporting=True,
            tag=None,
            dependencies=None
        ):

        stage = RunVisualiserStage(
                graph_id = graph_id,
                reporting = reporting,
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

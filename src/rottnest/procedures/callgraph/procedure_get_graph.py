from rottnest.procedures.utils.single_stage_procedure import SingleStageProcedure 
from .stage_get_graph import GetGraphStage

STAGE_TAG = 'get_graph_procedure'

GetGraphProcedure = SingleStageProcedure(
    'GetGraphProcedure',
    STAGE_TAG,
    GetGraphStage
)

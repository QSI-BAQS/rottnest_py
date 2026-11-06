from rottnest.procedures.utils.single_stage_procedure import SingleStageProcedure
#from rottnest.procedures.utils.stage_pool_task

from .stage_get_parameters import GetPostprocessorParametersStage 
from .stage_set_parameters import SetPostprocessorParametersStage 
from .stage_run_postprocessor import RunPostprocessorStage 

from rottnest.process_pool.process_pool import ComputeUnitExecutorPool


procedure_name = 'GetPostprocessorParametersProcedure'
GetPostprocessorParametersProcedure = SingleStageProcedure(procedure_name, None, GetPostprocessorParametersStage)

procedure_name = 'SetPostprocessorParametersProcedure'
SetPostprocessorParametersProcedure = SingleStageProcedure(procedure_name, None, SetPostprocessorParametersStage)

procedure_name = 'RunPostprocessorProcedure'
RunPostprocessorProcedure = SingleStageProcedure(procedure_name, None, RunPostprocessorStage)


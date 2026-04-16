from rottnest.procedures import procedure

from . import stage_set_error_budget


STAGE_TAG = 'set_error_budget_procedure'

class SetErrorBudgetProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(self, *, tag=None, dependencies=None, target_error=None, p_phys=None):

        stage = stage_set_error_budget.SetErrorBudgetStage(
                target_error = target_error,
                p_phys = p_phys,
                dependencies = []
        )

        stages = [
            stage
        ]
        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

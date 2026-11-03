from rottnest.plugins import plugin_managers
from rottnest.procedures.utils.single_stage_procedure import SingleStageProcedure

from . import factory

for manager in plugin_managers:
    cls_name = manager.__class__.__name__.split('Plugin')[0]
    stages = factory.option_stages_factory(cls_name, manager)

    for name, stage in stages.items():
        # Build procedure for each stage
        procedure_name = name.replace("Stage", "Procedure")
        procedure = SingleStageProcedure(procedure_name, None, stage)

        # Bind to namespace
        locals()[name] = stage
        locals()[procedure_name] = procedure 


from .procedure_synchronise_options import SynchroniseOptionsProcedure

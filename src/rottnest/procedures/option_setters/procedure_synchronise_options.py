from rottnest.procedures import procedure

# Forces factory resolution
from rottnest.procedures import option_setters

from rottnest.procedures.option_setters.base_synchronise_stage import SynchroniseOptionStage


STAGE_TAG = 'set_options_procedure'

class SynchroniseOptionsProcedure(procedure.RottnestCompilerProcedure): 
    '''
        Option setter procedure
        Builds a single synchronisation procedure from all 
        collected stages 
    '''
    TAG = STAGE_TAG

    def __init__(
            self,
            *,
            tag=None,
            dependencies=None, 
            **kwargs
        ):
        '''
            Constructor for the procedure
            Collects all constructors from the SetOptionStage            
            Matches the module tags to the kwargs of the procedure
            If tags match, implements the stage, otherwise empty elements
        
            This procedure requires that module strings in kwargs have keys of the form plugin_tag
        ''' 

        # Get the collected stages from subclasses of the base stage
        stage_constructors = SynchroniseOptionStage.get_collected_stages()

        stages = []
        for constructor in stage_constructors:

            # No stages share dependencies
            stages.append(
                constructor(
                    dependencies = [], 
                )
            )

        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)


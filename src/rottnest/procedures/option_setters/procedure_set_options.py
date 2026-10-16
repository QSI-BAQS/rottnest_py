from rottnest.procedures import procedure
from .base_set_option_stage import SetOptionStage


STAGE_TAG = 'set_options_procedure'

class SetOptionsProcedure(procedure.RottnestCompilerProcedure): 
    '''
        Option setter procedure
        Collects and dispatches all plugin option setters 
        Input is a dictionary containing plugin module tags
        as keys, and an option key / parameters tuple as 
        an argument
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
        stage_constructors = SetOptionStage.get_collected_stages()

        stages = []
        for constructor in stage_constructors:

            # Match the constructor to a kwargs key
            key = constructor.PLUGIN_MANAGER.get_plugin_tag()

            # Extract module strings from kwargs
            if key in kwargs:
                option_key, parameters = kwargs[key]
           
                # Use the constructor to build the stage and append to the list of stages 
                # No stages share dependencies
                stages.append(
                    constructor(
                        option_key,
                        parameters, 
                        dependencies = [], 
                    )
                )

        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)




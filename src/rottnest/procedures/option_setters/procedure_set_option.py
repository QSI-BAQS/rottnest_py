from rottnest.procedures import procedure
from .base_set_option_stage import SetOptionStage

STAGE_TAG = 'set_option_procedure'

class SetOptionProcedure(procedure.RottnestCompilerProcedure): 
    '''
        Option setter procedure
        Sets options for a single plugin type
        This is determined by the plugin_key
    '''
    TAG = STAGE_TAG

    def __init__(
            self,
            plugin_tag,
            option_key,
            parameters,
            *,
            tag=None,
            dependencies=None, 
            **kwargs
        ):
        '''
            Constructor for the procedure
            Collects all constructors from the LoadPluginModuleStage subclasses
            Matches the module tags to the kwargs of the procedure
            Performs the stage matching the plugin_tag       
        ''' 

        # Get the collected stages from subclasses of the base stage
        stage_constructors = SetOptionStage.get_collected_stages()
        stage_constructor = stage_constructors.get(plugin_tag, None)
        if stage_constructor is None:
            raise Exception(f"Unknown plugin tag: {plugin_tag}")
 
        stage = stage_constructor(option_key, parameters)
        super().__init__(None, stages=[stage], tag=tag, dependencies=dependencies)


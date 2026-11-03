from rottnest.procedures import procedure
from .base_load_modules_from_keys import LoadPluginModulesStage 


STAGE_TAG = 'load_modules_procedure'

class LoadModulesProcedure(procedure.RottnestCompilerProcedure): 

    TAG = STAGE_TAG

    def __init__(
            self,
            module_keys: dict,
            *,
            tag=None,
            dependencies=None, 
            **kwargs
        ):
        '''
            Constructor for the procedure
            Collects all constructors from the LoadPluginModuleStage subclasses
            Matches the module tags to the module_keys of the procedure
            If tags match, implements the stage, otherwise empty elements
        
            This procedure requires that module keys dict has keys of the form plugin_tag
        ''' 

        # Get the collected stages from subclasses of the base stage
        stage_constructors = LoadPluginModulesStage.get_collected_stages()

        stages = []
        for constructor in stage_constructors:

            # Match the constructor to a kwargs key
            key = constructor.PLUGIN_MANAGER.get_plugin_tag()

            # Extract module strings from kwargs
            # Default to empty to pick up any default
            # loading modules
            module_strings = []
            if key in module_keys:
                module_strings = module_keys[key]
           
            # Use the constructor to build the stage and append to the list of stages 
            # No stages share dependencies
            stages.append(
                constructor(
                    module_strings = module_strings,
                    dependencies = [], 
                )
            )

        super().__init__(None, stages=stages, tag=tag, dependencies=dependencies)

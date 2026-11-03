from .base_set_option_stage import SetOptionStage 
from .base_set_option_parameters_stage import SetOptionParametersStage
from .base_synchronise_stage import SynchroniseOptionStage
from .base_load_modules_from_keys import LoadPluginModulesStage 

TAG = 'TAG'
PLUGIN_MANAGER = 'PLUGIN_MANAGER'

def option_stages_factory(
        name: str,
        plugin_manager: "PluginManager"
    ) -> dict[str, "RottnestCompilerStages"]:
    '''
        Factory for building option setters 
        Generates everything from the plugin system 
        stages generated:
            - set_{}
            - set_{}_parameters
            - get_{}
            - get_{} 
            - synchronise
    '''

    def inject_init(self, *args, **kwargs):
        '''
            Deferred Init
            Injects the plugin manager reference
        '''
        super(self.__class__, self).__init__(
            plugin_manager,
            *args,
            **kwargs
        )
   
    base_factories = (
        SetOptionStage,
        SetOptionParametersStage,
        SynchroniseOptionStage,
        LoadPluginModulesStage,
    )

    # Create new types from the bases
    stages = {
        base.generate_class_name(name):
        type(
            base.generate_class_name(name), 
            (base,), 
            {
                TAG: base.generate_stage_tag(name),
                PLUGIN_MANAGER: plugin_manager,
            }
        )
        for base in base_factories 
    }

    # Inject the new init method
    for stage in stages.values():
        stage.__init__ = inject_init

    return stages


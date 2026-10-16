'''
    Stage for loading modules
'''
from rottnest.procedures import stage
from .utils import underscore_case


class LoadPluginModulesStage(stage.RottnestCompilerStage):
    '''
        Plugin loader stage
    '''
    _collector = set()

    def __init__(self, 
            plugin_manager: "PluginManager",
            module_strings: list[str],
             *, 
            tag=None, 
            dependencies=None
        ):
        self._plugin_manager = plugin_manager
        self._module_strings = module_strings
        
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def __init_subclass__(cls, **kwargs):
        '''
            Collector pattern
            Used to aggregate all loaders
        '''
        super().__init_subclass__(**kwargs)
        LoadPluginModulesStage._collector.add(cls)

    @classmethod
    def get_collected_stages(cls):
        '''
            Getter for collected stages
        '''
        return LoadPluginModulesStage._collected

    def execute(self, compiler_environment):
        '''
            Triggers the plugin manager 
        '''
        plugin_manager.load_modules_from_strings(*self._module_strings)
        self._complete = True

    @classmethod
    def generate_stage_tag(cls, name: str):
        '''
            Converts the name to underscore_case
        '''
        return f'load_{underscore_case(name)}_modules'

    @classmethod
    def generate_class_name(cls, name: str):
        '''
            Creates the name of the class
        '''
        return f'Load{name}ModulesStage'



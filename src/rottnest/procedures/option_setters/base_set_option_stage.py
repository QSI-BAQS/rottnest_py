'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from .utils import underscore_case

class SetOptionStage(stage.RottnestCompilerStage):
    '''
        Set option by key 
    '''
    # Collector pattern as class variable
    _collector = {} 

    def __init__(
            self,
            plugin_manager: "PluginManager", 
            option_key: str,
            option_params: dict = None,
            *,
            tag=None,
            dependencies=None,
        ):
        '''
            Constructor for set option
        '''

        self._plugin_manager = plugin_manager
        self._option_key = option_key
        if option_params is None:
            option_params = {}
        self._option_params = option_params
        
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
        key = cls.PLUGIN_MANAGER.get_plugin_tag()
        SetOptionStage._collector[key] = cls

    @classmethod
    def get_collected_stages(cls):
        '''
            Getter for collected stages
        '''
        return SetOptionStage._collector

    def execute(self, compiler_environment):
        '''
            Sets the plugin option 
        '''
        self._plugin_manager.set_current_option(
            self._option_key
        )

        if self._option_params is not None:
            self._plugin_manager.set_parameters(
                self._option_params
            )
        self._complete = True

    @classmethod
    def generate_stage_tag(cls, name: str):
        '''
            Converts the name to underscore_case
        '''
        return f'set_{underscore_case(name)}'

    @classmethod
    def generate_class_name(cls, name: str):
        '''
            Creates the name of the class
        '''
        return f'Set{name}Stage'

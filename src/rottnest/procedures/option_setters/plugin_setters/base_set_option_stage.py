'''
    Stage for setting layouts
'''
from rottnest.procedures import stage
from .utils import underscore_case

class SetOptionStage(stage.RottnestCompilerStage):
    '''
        Set option by key 
    '''

    def __init__(
            self,
            plugin_manager: "PluginManager", 
            option_key: str,
            *,
            option_params=None,
            tag=None,
            dependencies=None,
        ):

        self._plugin_manager = plugin_manager
        self._option_key = option_key
        self._option_params = option_params
        
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Sets the plugin option 
        '''
        self.plugin_manager.set_option(
            self._option_key
        )

        if self._params is not None:
            self.plugin_manager.set_parameters(
                **self._option_params
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

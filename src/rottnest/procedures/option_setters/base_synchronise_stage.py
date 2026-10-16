'''
    Stage for synchronising the option module with the pool manager 
'''
from rottnest.procedures import stage
from rottnest.plugins import architectures
from .utils import underscore_case

class SynchroniseOptionStage(stage.RottnestCompilerStage):

    def __init__(
            self,
            plugin_manager: "PluginManager",
            *,
            tag=None,
            dependencies=None
        ):

        self._plugin_manager = plugin_manager
        
        if dependencies is None:
            dependencies = []
 
        super().__init__(
            tag=tag, 
            dependencies=dependencies,
            asynchronous=False
        )

    def execute(self, compiler_environment):
        '''
            Synchronises with the process pool  
        '''
        option = self._plugin_manager.get_current_option()
        plugin_type = self._plugin_manager.get_plugin_tag()
        parameters = option.get_parameters()

        from rottnest.process_pool import get_pool
        pool = get_pool()
        pool.set_option(plugin_type, option.get_name(), parameters)
        self._complete = True


    @classmethod
    def generate_stage_tag(cls, name: str):
        '''
            Converts the name to underscore_case
        '''
        return f'synchronise_{underscore_case(name)}'

    @classmethod
    def generate_class_name(cls, name: str):
        '''
            Creates the name of the class
        '''
        return f'Synchronise{name}Stage'

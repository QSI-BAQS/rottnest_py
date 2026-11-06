'''
    Stage for synchronising the option module with the pool manager 
'''
from rottnest.procedures import stage
from rottnest.plugins import executables 
from .utils import underscore_case

class SynchroniseOptionStage(stage.RottnestCompilerStage):
    '''
        Option synchronisation stage
    '''

    # Collector pattern
    _collector = set() 

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

    def __init_subclass__(cls, *args, **kwargs):
        '''
            Collector pattern
            Builds a synchronise all procedure
        '''
        super().__init_subclass__(*args, **kwargs)
        SynchroniseOptionStage._collector.add(cls)

    @classmethod
    def get_collected_stages(cls):
        '''
            Getter for the collector
        '''
        return SynchroniseOptionStage._collector

    def execute(self, compiler_environment):
        '''
            Synchronises with the process pool  
        '''
        option = self._plugin_manager.get_current_option()
        plugin_type = self._plugin_manager.get_plugin_tag()
        parameters = self._plugin_manager.get_parameters()

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

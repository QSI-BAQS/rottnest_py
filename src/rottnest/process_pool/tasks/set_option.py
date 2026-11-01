'''
    Module Synchronisation Command
'''
from .pool_task import PoolTask, PriorityWorkerTask

from rottnest.process_pool import commands
from rottnest.priority_process import commands as priority_commands

from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure
from rottnest.procedures.option_setters.procedure_set_option import SetOptionProcedure

from rottnest import plugins


class SetOptionTask(PriorityWorkerTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SET_OPTION

    @classmethod
    def get_priority_worker_command(cls) -> str:
        '''
            Command to be passed to the priority worker
        '''
        return priority_commands.SET_OPTION

    @classmethod
    def submit(
            cls,
            plugin_manager: "PluginManager",
            *args,
            **kwargs
        ):
        '''
            Build submission from the plugin manager
        '''
        tag = plugin_manager.get_plugin_tag()
        option_key, parameters = plugin_manager.get_state()
 
        return super().submit(tag, option_key, parameters)

    def task(
            self,
            pool_manager: "PoolManager",
            plugin_tag: str,
            option_key: str,
            option_params: dict,
            *args,
            **kwargs
    ):
        '''
           Synchronises modules from the front end 
        ''' 
        # Update module plugin state
        proc = SetOptionProcedure(plugin_tag, option_key, option_params)
        proc.execute()

        # Maintain synchronisation 
        # with priority task
        pool_manager.submit_priority(
            self.get_priority_worker_command(), 
            plugin_tag,
            option_key,
            option_params
        )

        # Decomposition patch on executable update
        if plugin_tag == plugins.executables.get_plugin_tag():
            DecompositionPatchProcedure().execute()


class SetOptionsTask(PoolTask):
    '''
        Sets multiple options
    '''
    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SET_OPTIONS

    @classmethod
    def submit(
        cls,
        *args,
        **kwargs
    ):
       
        options = plugins.get_state()
        return super().submit(options)

    def task(
            self,
            pool_manager,
            options: dict[str, tuple],
            *args,
            **kwargs
        ):

        task = SetOptionTask()

        for plugin_tag, option in options.items():
            task(pool_manager, plugin_tag, *option)


class GetOptionsTask(PoolTask):
    '''
        Gets the synchronisation state of the manager 
        ## Currently only used for testing
    '''
    EXPECT_RESPONSE = True

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_OPTIONS

    def task(
            self,
            pool_manager,
            *args,
            **kwargs
        ):
        '''
            Gets the state of each option
        '''
        return plugins.get_state()


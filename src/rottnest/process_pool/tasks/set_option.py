'''
    Module Synchronisation Command
'''
from .pool_task import PoolTask

from rottnest.process_pool import commands
from rottnest.priority_process import commands as priority_commands

from rottnest.procedures.decomposition_patchers import DecompositionPatchProcedure
from rottnest.procedures.option_setters.procedure_set_option import SetOptionProcedure

from rottnest import plugins


class SetOptionTask(PoolTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SET_OPTION

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
        pool_manager.priority_task_queue.put((
            priority_commands.SET_OPTION,
            plugin_tag,
            option_key,
            option_params
        ))

        # Decomposition patch on executable update
        if plugin_tag == plugins.executables.get_plugin_tag():
            DecompositionPatchProcedure().execute()


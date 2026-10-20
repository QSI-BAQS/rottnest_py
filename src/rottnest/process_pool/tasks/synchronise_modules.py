'''
    Module Synchronisation Command
'''
from .pool_task import PoolTask

from rottnest.process_pool import commands
from rottnest.priority_process import commands as priority_commands
from rottnest.procedures.option_setters.procedure_load_modules import LoadModulesProcedure
from rottnest import plugins

class SynchroniseModulesTask(PoolTask):
    '''
       Synchronises modules 
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SYNCHRONISE_MODULES

    @classmethod
    def submit(
        cls,
        *args,
        **kwargs
    ):
        '''
            Gets the module keys for synchronisation 
        '''
        return super().submit(
            plugins.get_module_keys()
        )

    def task(
            self,
            pool_manager: "PoolManager",
            module_keys: dict,
            *args,
            **kwargs
        ):
        '''
           Synchronises modules from the front end 
        ''' 
        # Update module plugin state     
        proc = LoadModulesProcedure(module_keys)
        proc.execute()

        # These should have updated from the previous procedure
        module_keys = plugins.get_module_keys()

        # Maintain synchronisation with priority task
        pool_manager.priority_task_queue.put((
            priority_commands.SYNCHRONISE_MODULES,
            module_keys
        ))


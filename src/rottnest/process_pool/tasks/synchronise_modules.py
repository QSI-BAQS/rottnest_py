'''
    Module Synchronisation Command
'''
from rottnest.priority_process import commands as priority_commands
from rottnest.procedures.option_setters.project_setters import LoadModulesProcedure
from rottnest import plugins

'''
   Synchronises modules 
'''

def task_synchronise_modules(
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
    self.priority_task_queue.put((
        priority_commands.SYNCHRONISE_MODULES,
        modules_keys
    ))


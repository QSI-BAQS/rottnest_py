'''
    Run Sequence task
    Triggers a compilation
'''
from .pool_task import PoolTask
from rottnest.process_pool import commands

class RunSequenceTask(PoolTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.RUN_SEQUENCE

    def task(
            self,
            pool_manager: "PoolManager",
            layout_ids: list,
            *args,
            **kwargs
    ):
        '''
            Stops the workers
        '''
        
        # This is better handled inside the pool
        # manager's context
        return pool_manager.run_sequence(layout_ids)

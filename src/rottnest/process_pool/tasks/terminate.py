'''
    Terminates the pool 
'''

from rottnest.process_pool import commands, symbols
from .pool_task import PoolTask

class TerminateTask(PoolTask):
    '''
        Terminates the pool 
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.TERMINATE

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        pool_manager._task_stop_workers()
        pool_manager.stop_priority_worker()
        pool_manager.manager_running = False
        return True


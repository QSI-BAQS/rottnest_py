'''
    Simple ping task
'''
from .pool_task import PoolTask

from rottnest.process_pool import commands, symbols

class PingTask(PoolTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.PING

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        # Requires that the pool is running
        assert pool_manager.pool_running

        # This should not block
        pool_manager.worker_task_queue.put((commands.PING,))
        res = pool_manager.worker_ipc.get_item(
            commands.PING,
            blocking=True
        )
        assert res == symbols.PONG
        return symbols.PONG


class PingManagerTask(PoolTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.PING_MANAGER

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        '''
            Manager returns PONG
        '''
        return symbols.PONG


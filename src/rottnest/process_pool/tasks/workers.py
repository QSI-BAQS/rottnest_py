'''
    Simple ping task
'''


from rottnest.process_pool import commands, symbols

from .pool_task import PoolTask

class StartWorkersTask(PoolTask):
    '''
        Sets a plugin module option
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.START_WORKERS

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        if pool_manager.pool_running:
            # Workers already running, return
            return

        # In function imports allow the tasks to be
        # double sided without circulars 
        from rottnest.process_pool.entrypoints import pool_worker 
        from rottnest.compute_units.layout_proxy import LayoutProxy

        entrypoint = pool_worker.get_entrypoint()
        layouts = LayoutProxy.get_layouts()
        
        pool_manager.start_workers(
            entrypoint,
            layouts
        )


class StopWorkersTask(PoolTask):
    '''
        Sets a plugin module option
    '''
    EXPECT_RESPONSE = True 

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.STOP_WORKERS

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        '''
            Stops the workers
        '''
        
        # This is better handled inside the pool
        # manager's context
        return pool_manager.stop_workers()

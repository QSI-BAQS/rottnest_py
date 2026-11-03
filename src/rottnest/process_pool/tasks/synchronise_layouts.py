'''
    Layout Synchronisation Command
'''
from .pool_task import PriorityWorkerTask 

from rottnest.process_pool import commands
from rottnest.priority_process import commands as priority_commands

from rottnest.compute_units.layout_proxy import LayoutProxy

class SynchroniseLayoutsTask(PriorityWorkerTask):
    '''
       Synchronises modules 
    '''

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SYNCHRONISE_LAYOUTS

    @classmethod
    def get_priority_worker_command(cls) -> str:
        return priority_commands.SYNCHRONISE_LAYOUTS

    @classmethod
    def submit(
        cls,
        *args,
        **kwargs
    ):
        '''
            Gets the module keys for synchronisation 
        '''
        layout_payload = list(LayoutProxy.get_layouts())
        return super().submit(
            layout_payload 
        )

    def task(
            self,
            pool_manager: "PoolManager",
            layouts: list[int, "Layout"],
            *args,
            **kwargs
        ):
        '''
           Synchronises modules from the front end 
        ''' 

        for layout_id, layout_json in layouts:
            LayoutProxy.add_layout_with_id(
                layout_id, layout_json
            )
            obj = LayoutProxy.get_layout(layout_id)
       
        # Synch with priority worker
        pool_manager.submit_priority(
            self.get_priority_worker_command(),
            list(LayoutProxy.get_layouts())
        ) 

'''
    Layout Synchronisation Command
'''
from .pool_task import PoolTask

from rottnest.process_pool import commands
from rottnest.priority_process import commands as priority_commands

from rottnest.compute_units.layout_proxy import LayoutProxy

class SynchroniseLayoutsTask(PoolTask):
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
    def submit(
        cls,
        *args,
        **kwargs
    ):
        '''
            Gets the module keys for synchronisation 
        '''
        layout_payload = list(LayoutProxy.get_layouts())
        print("LAYOUTS: ", layout_payload)
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

        # Dispatch to priority task
        pool_manager.priority_task_queue.put((
            priority_commands.SYNCHRONISE_LAYOUTS,
            list(LayoutProxy.get_layouts())
        ))


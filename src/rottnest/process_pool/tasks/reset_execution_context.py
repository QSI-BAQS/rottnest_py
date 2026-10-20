'''
    Module Synchronisation Command
'''
from .pool_task import PoolTask

from rottnest.process_pool import commands

from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser

class ResetExecutionContextTask(PoolTask):
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
            *args,
            **kwargs
    ):
        '''
            Resets execution context tracking
        '''
        PyliqtrParser.force_cache_flush()

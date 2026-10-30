'''
    Simple ping task
'''

from rottnest.process_pool import commands, symbols
from .pool_task import PoolTask

class GetSynchronisationStatus(PoolTask):
    '''
        Sets a plugin module option
    '''
    EXPECT_RESPONSE = True

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.SYNCHRONISATION_STATUS

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        ''' 
        '''
        # TODO


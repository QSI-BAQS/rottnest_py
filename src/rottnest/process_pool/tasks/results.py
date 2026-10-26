'''
    Results handler tasks
'''
from rottnest.process_pool import commands
from .pool_task import PoolTask

class GetCurrentResultsTask(PoolTask):
    '''
       Gets the current results 
    '''
    EXPECT_RESPONSE = True

    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_CURRENT_RESULTS

    def task(
            self,
            pool_manager: "PoolManager",
            *args,
            **kwargs
    ):
        '''
            Returns manager status
        '''
        return pool_manager.get_current_results() 

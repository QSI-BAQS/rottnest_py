'''
    Visualiser Tasks
'''

from rottnest.priority_process import commands
from .pool_task import PoolTask

class GetVisualiserTask(PriorityPoolTask):
    '''
        Sets a plugin module option
    '''
    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_VISUALISER

class GetVisualiserNextTask(PriorityPoolTask):
    '''
        Sets a plugin module option
    '''
    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_VISUALISER_NEXT

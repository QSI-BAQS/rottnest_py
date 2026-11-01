'''
    Visualiser Tasks
'''

from rottnest.priority_process import commands
from .pool_task import PriorityWorkerTask

class GetVisualiserTask(PriorityWorkerTask):
    '''
        Sets a plugin module option
    '''
    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_VISUALISER

class GetVisualiserNextTask(PriorityWorkerTask):
    '''
        Sets a plugin module option
    '''
    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_VISUALISER_NEXT

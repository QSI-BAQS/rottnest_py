'''
    Callgraph Tasks
'''

from rottnest.priority_process import commands
from .pool_task import PriorityWorkerTask 

class GetCallgraphTask(PriorityWorkerTask):
    '''
        Sets a plugin module option
    '''
    @classmethod
    def get_command(cls) -> str:
        '''
            Associated Command
        '''
        return commands.GET_CALLGRAPH


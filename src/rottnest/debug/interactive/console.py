

from rottnest.debug.handlers import DebugConsoleHandler
from rottnest.debug.interactive.plugin import DebugPluginHandler


class DebugConsoleSystem:
    
    @staticmethod
    def default(app=None):
        '''
           Gets the default of the console handler 
        '''
        cons = DebugConsoleHandler(app)\
        .attach('plugin', DebugPluginHandler.make())
        
        # setup handlers
        return cons

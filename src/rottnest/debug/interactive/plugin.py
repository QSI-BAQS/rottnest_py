

from rottnest.debug.handlers import DebugConsoleHandler, DebugCommand, DebugHandler

def plugin_load_cfg(app, args):

    return True

def plugin_load(app, args):

    return True

def plugin_dumps(app, args):

    return True


class DebugPluginHandler:

    @staticmethod
    def make():
        '''
           Creates a plugin handler that will
           build in some commands to allow it to interact with
           the rest of the system 
        '''
        handler = DebugHandler('plugin')\
        .add_command('plugin', DebugPluginHandler.cmd(['loadcfg', ], \
                                                      plugin_load_cfg))\
        .add_command('plugin', DebugPluginHandler.cmd(['load'], plugin_load))\
        .add_command('plugin', DebugPluginHandler.cmd(['dump'], plugin_dumps))
        return handler
        
        
    @staticmethod
    def cmd(params, hook, suffix='', description=''):
        '''
           Makes the command
        '''
        cmd = DebugCommand(str(DebugCommand.__name__), params, hook, suffix,\
                           description)

        return cmd

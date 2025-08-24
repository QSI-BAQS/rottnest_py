

from rottnest.debug.handlers import DebugCommand, DebugHandler

def plugin_load_cfg(app, args):
    print("Loading config")
    return True

def plugin_load(app, args):

    print("Loading module")
    return True

def plugin_dumps(app, args):
    print(dir(app))
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
        .add_command('plugin-loadcfg', DebugPluginHandler.cmd(['loadcfg', ], \
                                                      plugin_load_cfg))\
        .add_command('plugin-loadmodule', DebugPluginHandler.cmd(['loadmodule'], plugin_load))\
        .add_command('plugin-dumps', DebugPluginHandler.cmd(['dumps'], plugin_dumps))
        return handler
        
        
    @staticmethod
    def cmd(params, hook, suffix='', description=''):
        '''
           Makes the command
        '''
        cmd = DebugCommand('plugin-'+params[0], params, hook, suffix,\
                           description)

        return cmd

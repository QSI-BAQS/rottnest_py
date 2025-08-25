

from rottnest.debug.handlers import DebugCommand, DebugHandler

def plugin_loadcfg(app, args):
    '''
       Debug command that allows me to load from a configuration file
       and debug modules 
    '''
    extensions = app.get_extensions()
    amap = extensions.get_arch_map()
    amap.load_config('archconfig.txt')
    return True

def plugin_load(app, args):

    print("Loading module")
    return True

def plugin_dumps(app, all_args):
    route = []
    args = all_args[0].split('.')
    if args[0].rstrip() != 'self':
        route.append(args[0].rstrip())
    for kidx in range(1, len(args)):
        route.append(args[kidx].rstrip())

    # get entry
    valid = True
    current = app
    for k in route:
        if k in current.__dict__:
            current = current.__dict__[k]
        else:
            print('Unable to retrieve key ' + k + " on object")
            valid = False
    if valid:
        print(dir(current))
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
        .add_command('plugin-loadcfg', DebugPluginHandler.cmd(['loadcfg'], \
                                                      plugin_loadcfg))\
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

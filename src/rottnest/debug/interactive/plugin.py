

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

def plugin_load_tscheduler(app, args):
    extensions = app.get_extensions()
    amap = extensions.get_arch_map()
    amap.load_config('arch.cfg')
    print(str(amap.get_architectures()['Four Stage Superconducting'].designer.get_designer_metadata()))
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
        .add_command('plugin-loadcfg', DebugPluginHandler.cmd('loadcfg', ['loadcfg'], \
                                                      plugin_loadcfg))\
        .add_command('plugin-tsched', DebugPluginHandler.cmd('tsched', ['Y'], plugin_load_tscheduler))\
        .add_command('plugin-dumps', DebugPluginHandler.cmd('dumps', ['dumps'], plugin_dumps))
        return handler
        
        
    @staticmethod
    def cmd(name, params, hook, suffix='', description=''):
        '''
           Makes the command
        '''
        cmd = DebugCommand('plugin-'+name, params, hook, suffix,\
                           description)

        return cmd

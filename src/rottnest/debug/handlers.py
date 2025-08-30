import selectors
import sys

class DebugConsoleHandler:
    '''
        Used as part of stdin interaction
    '''
    def __init__(self, app=None):
        self.handlers = {}
        self.app = app
        self.stdin = sys.stdin
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.stdin, selectors.EVENT_READ, DebugConsoleHandler.stdin_event)


    @staticmethod
    def stdin_event(data, mask):
        '''
           Gets the line that was ready 
        '''
        line = sys.stdin.readline()
        return line

    def get_app(self):
        '''
           Gets the application it is hooked with 
        '''
        return self.app

    def set_app(self, app):
        '''
           Sets the application if it is initialised late 
        '''
        self.app = app

    def get_handler(self, key):
        '''
           Gets the handler associated with the
           key 
        '''
        if key in self.handlers:
            return self.handlers[key]
        return None

    def attach(self, key, handler):
        '''
           Attaches a handler to the console handler
           returns self
        '''
        self.handlers[key] = handler
        return self

    def all_handlers(self):
        '''
           Gets all the handlers attached 
        '''
        return self.handlers

    def selector_interact(self):
        '''
           Selector/event look here 
        '''
        while True:
            res = self.selector.select(4)
            for (k, mask) in res:
                stdin_cb = k.data
                line = stdin_cb(k.data, mask)
                self.interact(line)

    def interact(self, line):
        '''
           Creates an interactive shell for working
           with the server 
        '''
        spl = line.split(' ')
        if len(spl) >= 1:
        
            cmd = spl[0].rstrip()
            cmd_key = cmd
            cmd_mod_key = cmd
            if '-' in cmd:
                cmd_mod_key = cmd_key.split('-')[0]
            if cmd_mod_key in self.handlers:
                handler = self.handlers[cmd_mod_key]
                if cmd_key in handler.get_commands():
                    cmdobj = handler.get_command(cmd_key)
                    cmdobj.parse_and_run(line, self.get_app())
                else:
                    print("Unknown command: " + cmd_key)
            else:
                print("Unknown command group: " + cmd_mod_key)

    def interact_closure(self):
        '''
           Provides an interact closure for event systems 
        '''
        ref = self
        def ref_interact():
            ref.selector_interact()

        return ref_interact

class DebugCommand:
    '''
       DebugCommand that will allow re-hits and state information
       to be exposed via this console 
    '''

    def __init__(self, cmdname, params, hook, suffix='', desc=''):
        self.cmdname = cmdname
        self.params = params
        self.hook = hook
        self.suffix = suffix
        self.description = desc

    def get_description(self):
        '''
           gets the description of the debug command 
        '''
        return self.description


    def get_fullcmd(self):
        '''
           Prints the full command (including suffix) 
        '''
        return self.cmdname + self.suffix
        

    def parse_and_run(self, line, app):
        '''
           Parses the line and tries to detect the
           correct number of arguments to params given
           and if the cmd is correct 
        '''
        spl = line.split(' ')
        if len(spl) > 0:
            input_cmd = spl[0]

            n_params = len(self.params)
            fullcmd = self.cmdname + self.suffix
            if fullcmd == input_cmd and n_params == (len(spl)-1):
                args = []
                if len(spl) > 1:
                    args = spl[1:]
                
                return self.hook(app, args)

        
        return False
        

class DebugHandler:
    '''
       DebugHandlers are there to assist with
       reloading, testing and interacting with the system
       while it is live 
    '''

    def __init__(self, rootkey):
        self.rootkey = rootkey
        self.commands = {}


    def register_with(self, console):
        '''
            Registers the handler with the console
        '''
        console.attach(self.rootkey, self)
        
    def get_commands(self):
        '''
           Gets the map of commands associated with
           the handler 
        '''
        return self.commands

    def get_command(self, cmd):
        '''
            Gets the command based on the command key
        '''
        if cmd in self.commands:
            cmdobj = self.commands[cmd]
            return cmdobj
        return None

    def add_command(self, key, cmd):
        '''
           Adds a command to the map
           and returns self (builder) 
        '''
        self.commands[key] = cmd
        return self

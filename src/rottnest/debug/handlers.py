import os
import sys
import selectors

class SelectorComposite:
    '''
       SelectorComposite is used to have an object with
       pid, file-descriptor and handler function upon event 
    '''
    def __init__(self, pid, fileobject, operfn, selector):
        self.pid = pid
        self.fileobject = fileobject
        self.operfn = operfn
        self.selector = selector

    def as_tup(self):
        '''
           Returns the fields as a tuple 
        '''
        return (self.pid, self.fileobject, self.operfn, self.selector)

class DebugConsoleHandler:
    '''
        Used as part of stdin interaction
    '''
    def __init__(self, *, app=None, monitor=None, disabled=False):
        '''
            Initialisation but also needs to handle the
            possibility that when forked, the handler could be
            listening for stdin and likely trigger multiple consumer issues
        '''
        
        self.pid = os.getpid() # Needed for disengaging if hooked with fork
        self.handlers = {}
        self.monitor = monitor
        self.app = app
        self.stdin = sys.stdin
        self.selector = selectors.DefaultSelector()
        # NOTE: pytest doesn't like stdin capture, we want to
        # ensure we don't conflict with it
        # 
        # Make sure you mock `self.stdin` inside your test
        # cases

        selector_data = SelectorComposite(self.pid, sys.stdin, \
                                      DebugConsoleHandler.stdin_event, \
                                      self.selector)

        def _event_hook(data, mask):
            '''
               Closure constructed to not disrupt too much
               in the other parts of the codebase 
            '''
            sel_data = selector_data
            (pid, fileobject, operfn, selector) = sel_data.as_tup()

            npid = os.getpid()

            if npid != pid:
                # Deregister from selector
                selector.unregister(fileobject)
            else:
                return operfn(sel_data.as_tup(), mask)
        
        if 'pytest' not in sys.modules and not disabled:
            self.selector.register(self.stdin, selectors.EVENT_READ, _event_hook)


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
        return self

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

    def get_monitor(self):
        '''
          Gets the monitor, assuming it has been hooked correctly  
        '''
        return self.monitor

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

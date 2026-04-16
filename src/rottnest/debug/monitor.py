import sys
from time import time
from .interactive.console import DebugConsoleSystem
from os import getpid

class DebugMonitorMessage:
    '''
       MonitorMesasge that will generate a timestamp
       and the data associated 
    '''

    def __init__(self, message, kind='', tabsize=4, charcount=56):
        '''
           message itself along with generating the timestamp 
        '''
        self.kind = kind
        self.message = message
        self.timestamp = time()
        self.tabsize = tabsize
        self.charcount = charcount
        self.pid = getpid()

    def fmtstr(self):

        '''
           String representation of the message itself
           Formats it as a debug message
        '''
        kind = self.kind
        timestamp = self.timestamp
        message = self.message
        msglen = len(message)

        parts = msglen / self.charcount
        start = 0
        end = self.charcount
        message_comp = ''
        spaced_tab = ' ' * (self.tabsize * 4)
        
        if parts >= 1:
            i = 0
            while(i < parts):
                segment = message[start:end]
                start = end
                end += self.charcount
                if i >= 1:
                    message_comp += f"{spaced_tab}{segment}\n"
                else:
                    message_comp += f"{segment}\n"
                i += 1
        else:
            message_comp = message
        
        return f"(DEBUG:{int(timestamp)}, {self.pid}, {kind}): {message_comp}"

    @staticmethod
    def make(kind, message):
        '''
           Gets events that occur and planted within the codebase 
        '''
        return DebugMonitorMessage(message, kind)  

    def __repr__(self):
        '''
           repr call for fmtstr 
        '''
        return self.fmtstr()


    def __str__(self):
        '''
           str call for fmtstr 
        '''
        return self.fmtstr()


class DebugMonitor:
    '''
      Debug monitor object is used to retrieve data
      regarding certain call points to ensure that it is able to
      extract meaningful information  
    '''

    def __init__(self, use_stdin=True, stdout_output=True, to_file=None,\
                  use_decorator=True, error_filepath: str | None =None):
        '''
           Initialises the debug monitor to ensure we can
           interaction and retrieve the log or dump it to a file 
        '''
        self.error_filepath: str = f"debug_error-{time()}.log" \
            if error_filepath is None else error_filepath

        self.use_stdin = use_stdin
        self.stdout_output = stdout_output
        self.to_file = to_file
        self.disabled = False
        self.logs = []
        self.use_decorator = use_decorator
        self.console = DebugConsoleSystem.default(monitor=self, disabled=self.disabled)


        

    @staticmethod
    def current() -> 'DebugMonitor':
        '''
           Gets the global singleton instance 
        '''
        return sys.modules[__name__].__dict__['__debug_monitor']

    @staticmethod
    def default():
        '''
           Initialises a debug monitor with default settings
           If initialised, it will return the same object
        '''
        modvar = sys.modules[__name__]
        if '__debug_monitor' not in modvar.__dict__:
            mon = DebugMonitor()
            mon.log(DebugMonitorMessage.make('Startup', 'Monitor constructed'))
            return mon
        else:
            return sys.modules[__name__].__dict__['__debug_monitor']

    

    @staticmethod
    def with_obj(obj, kind=''):
        '''
           Receives an object and will format it and allow for output  
        '''
        sfmt = repr(obj)
        dbmsg = DebugMonitorMessage(sfmt, kind)
        mon = DebugMonitor.current() 
        mon.log(dbmsg)


    @staticmethod
    def global_disable():
        '''
            Disables the global debug monitor
        '''
        __debug_monitor.disaled = True
        
    @staticmethod
    def global_enable():
        '''
            Enable the global debug monitor
        '''
        __debug_monitor.disaled = False

    @staticmethod
    def dump(message: str):
        '''
           Static method version of the dump_error,
           Ends up calling the singleton instance 
        '''
        inst = DebugMonitor.current()
        if not inst.disabled:
            inst.dump_error(message)

    def dump_error(self, message: str):
        '''
           Will dump an error log to the file
           This is a buffered operation but will call flush/close
           after write is called 
        '''
        with open(self.error_filepath, 'a') as f:
            f.write(f"{time()}{message}\n")
            

    def set_console_context(self, app):
        '''
           Assuming console is attached, we will set the application context
           for it 
        '''
        self.console.set_app(app)

    def is_using_decorator(self):
        '''
           Outlines if the decorator methods are being used
           for functions and methods 
        '''

        return self.use_decorator

    def set_use_decorator(self, to_use: bool):
        '''
           Simple setter to show if the decorator is being used 
        '''
        self.use_decorator = to_use

    def stdin_enabled(self):
        '''
           Checks to see if stdin is enabled 
        '''
        return self.use_stdin

    def disable(self):
        '''
           Disables logging that is occurring 
        '''
        self.disabled = True

    def get_console(self):
        '''
           Gets the console for debugging purposes 
        '''
        return self.console

    def enable(self):
        '''
           Enables the logging 
        '''
        self.disabled = False

    def log(self, message: DebugMonitorMessage):
        '''
           Logs a message that is given to it, will print it if it
           has been enabled
        '''
        if self.stdout_output and not self.disabled:
            print(message)
        if not self.disabled:
            self.logs.append(message)

    def all_logs(self):
        '''
          Gets all the logs that have been noted  
        '''
        for log in self.logs:
            print(str(log))

    def write_to_file(self):
        '''
           If `to_file` is not None and bound to a path/string
           It will save the contents and write it to a file 
        '''
        if self.to_file and isinstance(self.to_file, str) and not self.disabled:
            with open(self.to_file) as f:
                for log in self.logs:
                    f.write(log)
        else:
            print("path has not been set")

    def set_filepath(self, path: str):
        '''
           Sets the path where it will write out the data 
        '''
        self.to_file = path

    def clear(self):
        '''
           Clears all the logs within the monitor 
        '''
        self.logs = []


'''
   Global debug monitor that can be used 
'''
__debug_monitor = DebugMonitor.default()

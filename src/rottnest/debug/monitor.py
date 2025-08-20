import sys
from time import time

class DebugMonitorMessage:
    '''
       MonitorMesasge that will generate a timestamp
       and the data associated 
    '''

    def __init__(self, message, kind=''):
        '''
           message itself along with generating the timestamp 
        '''
        self.kind = kind
        self.message = message
        self.timestamp = time.time()

    def fmtstr(self):

        '''
           String representation of the message itself 
        '''
        kind = self.kind
        timestamp = self.timestamp
        message = self.message
        return f"(DEBUG:{kind}) {timestamp}: ${message}"

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

    def __init__(self, use_stdin=False, stdout_output=True, to_file=None):
        '''
           Initialises the debug monitor to ensure we can
           interaction and retrieve the log or dump it to a file 
        '''
        self.use_stdin = use_stdin
        self.stdout_output = stdout_output
        self.to_file = to_file
        self.disabled = False
        self.log = []


    @staticmethod
    def current():
        '''
           Gets the global singleton instance 
        '''
        return __debug_monitor

    @staticmethod
    def default():
        '''
           Initialises a debug monitor with default settings
           If initialised, it will return the same object
        '''
        modvar = sys.modules[__name__]
        if '__debug_monitor' not in modvar.__dict__:
            return DebugMonitor()
        else:
            return __debug_monitor

    @staticmethod
    def with_obj(obj, kind=''):
        '''
           Receives an object and will format it and allow for output  
        '''
        sfmt = repr(obj)
        dbmsg = DebugMonitorMessage(sfmt, kind)
        __debug_monitor.log(dbmsg)


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

    def disable(self):
        '''
           Disables logging that is occurring 
        '''
        self.disabled = True


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
            self.log.append(message)


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

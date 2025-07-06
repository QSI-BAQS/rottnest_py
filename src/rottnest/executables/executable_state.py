from rottnest.executables.current_executable import current_executable

class ExecutableState:

    def __init__(self, prg=current_executable, args=[10, 1.0, 0.95]):
        '''
           Designed to replace the executable state instead of
           current_executable module  
        '''

        self.prg = prg
        self.args = args
        
    def set_program(self, prg, args):
        '''
           Sets the current program reference
           and the arguments with it

           This is a weak reference, this will be resolved
           with the exe_map 
        '''
        self.prg = prg
        self.args = args

    def get_program(self):
        '''
           Gets the currently selected program
           on the backend, simply returns a dictionary  
        '''
        return {
            "prg_name": self.prg,
            "prg_args": self.args
        }

    def invoke_with(self, exe_map):
        '''
           Invokes with the exe_map, makes sure it can be
           resolved 
        '''

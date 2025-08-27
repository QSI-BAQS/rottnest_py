
class ExecutableState:

    def __init__(self, name=None, prg=None, args=[], params=[]):
        '''
           Designed to replace the executable state instead of
           current_executable module  
        '''
        self.name = name
        self.prg = prg
        self.args = args
        self.params = params
        
    def set_program(self, name, prg, args, params):
        '''
           Sets the current program reference
           and the arguments with it

           This is a weak reference, this will be resolved
           with the exe_map 
        '''
        self.name = name
        self.prg = prg
        self.args = args
        self.params = params;

    def get_program(self):
        '''
           Gets the currently selected program
           on the backend, simply returns a dictionary  
        '''
        return {
            "prg_name": self.name,
            "prg_params": self.params,
            "prg_args": self.args
        }

    def invoke_with(self, app):
        '''
           Invokes with the exe_map, makes sure it can be
           resolved and invoked
        '''
        response = {
            "success": False,
            "message": "Program was not invoked"
        }
        prginst = app.get_extensions().get_exe_map().make_instance_from(self.prg, self.args)

        if prginst is not None:

            #TODO: We need to monitor this object
            #prginst.invoke()
            
            response = {
                "success": True,
                "message": "Program was invoked"
            }

        return response

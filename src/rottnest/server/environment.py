import os

class ServerEnvironmentSettings:
    '''
       ServerEnviromentSettings

       Allows for some sensible defaults that can be set for the
       application
    '''

    _instance = None
    
    def __init__(self, numpy_processes=1, mpl_backend="Agg"):
        '''
           Initialises the server environment settings with defaults
           unless it is specified to be overloaded 
        '''
        self.environment_set = False
        self.numpy_processes = numpy_processes
        self.mpl_backend = mpl_backend
        self.environment_dict = {
            "OMP_NUM_THREADS": f"{numpy_processes}",
            "MPLBACKEND" : f"{mpl_backend}"
        }

    @classmethod
    def get_instance(cls):
        '''
           Gets the singleton instance for the environment variables 
        '''
        current_instance = ServerEnvironmentSettings._instance
        if current_instance is None:
            current_instance = ServerEnvironmentSettings()
            current_instance._set_environment_variables()   
            ServerEnvironmentSettings._instance = current_instance

        return current_instance


    def _set_environment_variables(self):
        '''
           Sets the environment variables for the server 
        '''
        for (k, v) in self.environment_dict.items():
            os.environ[k] = v


# Immediately invokes the get_instance and processes the environment variables
__server_env_instance = ServerEnvironmentSettings.get_instance()

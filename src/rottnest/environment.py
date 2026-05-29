import os

from rottnest.config import OMP_NUM_THREADS, MPLBACKEND

class EnvironmentSettings:
    '''
       EnviromentSettings

       Allows for some sensible defaults that can be set for the
       application
    '''

    _instance = None
    
    def __init__(
            self,
            numpy_processes=None,
            mpl_backend=None
        ):
        '''
           Initialises the server environment settings with defaults
           unless it is specified to be overloaded 
        '''
        self.environment_set = False
        if numpy_processes is None:
            numpy_processes = OMP_NUM_THREADS
        if mpl_backend is None:
            mpl_backend = MPLBACKEND

        self.numpy_processes = numpy_processes
        self.mpl_backend = mpl_backend
        self.environment_dict = {
            "OMP_NUM_THREADS": f"{numpy_processes}",
            "MPLBACKEND" : f"{mpl_backend}"
        }
        self._set_environment_variables()

    @classmethod
    def get_instance(cls):
        '''
           Gets the singleton instance for the environment variables 
        '''
        
        if cls._instance is None:
            cls._instance = EnvironmentSettings()
        return cls._instance 


    def _set_environment_variables(self):
        '''
           Sets the environment variables for the server 
        '''
        for (k, v) in self.environment_dict.items():
            os.environ[k] = v


# Immediately invokes the get_instance and processes the environment variables
__env_instance = EnvironmentSettings.get_instance()

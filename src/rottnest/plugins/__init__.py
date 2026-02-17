from .architecture_plugins import ArchitecturePlugins
from .executable_plugins import ExecutablePlugins

print("INIT PLUGINS")

def override_architectures(architectures_override: ArchitecturePlugins):
    '''
       Allows for overriding the architecture plugins 
    '''
    global architectures
    architectures = architectures_override
    
def override_executables(executables_override: ExecutablePlugins):
    '''
       Allows for overriding the architecture plugins 
    '''
    global executables
    executables = executables_override

executables = ExecutablePlugins.default_loader()
architectures = ArchitecturePlugins.default_loader()

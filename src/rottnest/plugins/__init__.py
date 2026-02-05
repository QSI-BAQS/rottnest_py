from .architecture_plugins import ArchitecturePlugins
from .executable_plugins import ExecutablePlugins

print("INIT PLUGINS")

executables = ExecutablePlugins.default_loader()
architectures = ArchitecturePlugins.default_loader()

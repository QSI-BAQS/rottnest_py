from .architecture_plugins import ArchitecturePlugins
from .executable_plugins import ExecutablePlugins

executables = ExecutablePlugins.default_loader()
architectures = ArchitecturePlugins.default_loader()

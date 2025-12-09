from .architecture_plugins import ArchitecturePlugins
from .executable_plugins import ExecutablePlugins
from .config_loader import _load_default_config

executables = ExecutablePlugins()
architectures = ArchitecturePlugins()


def load_default_architecture_config():
    _load_default_config(architectures._config_file_name, architectures)


def load_default_executable_config():
    _load_default_config(executables._config_file_name, executables)

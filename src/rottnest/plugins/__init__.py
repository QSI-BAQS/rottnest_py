from .architecture_plugins import ArchitecturePlugins
from .executable_plugins import ExecutablePlugins
from .config_loader import _load_default_config

executables = ExecutablePlugins()
architectures = ArchitecturePlugins()


def load_default_architecture_config(config_name=None):
    config_name = architectures._config_file_name if config_name is None else config_name
    _load_default_config(config_name, architectures)


def load_default_executable_config(config_name=None):
    config_name = executables._config_file_name if config_name is None else config_name
    _load_default_config(config_name, executables)

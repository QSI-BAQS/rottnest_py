'''
    Tests recursively loading submodules with relative
    imports 

    This can be done using:
    `importlib.import_module(path, package)`

'''
from typing import Iterable
import pkgutil, importlib

def recurse_package(base_module: "module") -> Iterable[tuple["str", "package"]]:
    '''
        Generates all python files in the procedures directory
    '''
    for module in pkgutil.iter_modules(base_module.__path__):
        if not module.ispkg:
            path = f'.{module.name}'
            package = base_module.__package__
            yield (path, package)

        else:
            submodule = importlib.import_module(f'.{module.name}', base_module.__package__)
            yield from recurse_package(submodule)


'''
    Generic plugin manager class

    This only exists to avoid duplication between the execution and architecture plugin managers 
'''
import sys
import importlib

# Used for unique namespaces for dynamically loaded plugins
glb_counter = 0

class PluginManager:
    '''
       Architecture Plugin manager 
    '''

    def __init__(self, *, module_tag: str, modules: list):
        '''
            Generic plugin manager
            Used to manage loading resources from disparate modules
            :: module_tag : str :: Default tag for module level names of resources    
        '''
        self._modules = modules
        self._module_tag = module_tag

    def _load_objects(self, *modules) -> dict:
        '''
            Loads constructors from modules
        '''

        if len(modules) == 0:
            modules = self._modules

        loaded_objects = {} 
        for module in modules:
            plugin_targets = getattr(module, self._module_tag, None)

            # Module has no architectures exposed
            if plugin_targets is None:
                print(f"Module {module} does not contain any valid plugin targets")
                print(f'To expose an architecture at the module level, please set a "{self._module_tag}" variable in the module\'s main namespace (e.g. __init__.py)')
                continue

            for target in plugin_targets:
                try:
                    key = target.get_name()
                    loaded_objects[key] = target
                except AttributeError:
                    print(f"Object {target} in module {module} does not implement the required plugin interface")
        return loaded_objects

    def load_config(self, filepath: str) -> dict:
        '''
            Wrapper for loading from a config file
        '''
        try:
            modules = self._load_modules_from_config(
                filepath
            )
            module_objects = self._load_objects(
                *modules
            ) 
            return module_objects
        except FileNotFoundError:
            return FileNotFoundError

    @staticmethod
    def _load_modules_from_config(filepath) -> list:
        modules = []

        with open(filepath, 'r') as config:
            for entry in config: 
                entry = entry.strip('\n')
                module = None
                try:
                    module = PluginManager._load_module_from_module_string(entry)
                except:
                    pass

                try: 
                    module = PluginManager._load_module_from_file_path(entry)
                except:
                    pass

                if module is None:
                    print(f"Entry {entry} could not be processed")
                else:
                    modules.append(module)
        return modules

    @staticmethod
    def _load_module_from_file_path(filepath: str):
        '''
           Loads a python module from file 
           Calls `all_architectures()` and registers them
        '''
        # Load counter for unique namespacing
        global glb_counter
        plugin_name = f'dynamically_loaded_arch_{glb_counter}'
        glb_counter += 1

        spec = importlib.util.spec_from_file_location(plugin_name, filepath)
        plugin_obj = importlib.util.module_from_spec(spec)

        # NOTE: There should be better way instead of relying on sys here
        sys.modules[plugin_name] = plugin_obj
        spec.loader.exec_module(plugin_obj)

        return plugin_obj 

    @staticmethod
    def _load_module_from_module_string(module_name: str):
        '''
           Loads a python module from module space
           Calls `all_architectures()` and registers them
        '''
        module = importlib.import_module(module_name)
        return module

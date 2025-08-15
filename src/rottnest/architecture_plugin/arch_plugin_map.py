import sys
import importlib.util
import json

from ..architecture_interface.rottnest_architecture import ROTTNEST_ARCHITECTURE_MODULE_TAG
from rottnest.plugin.arch_location import ArchLocationKind

class ArchitecturePlugins:
    '''
       Architecture Plugin manager 
    '''

    def __init__(self):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin  
        '''

        # Load from config
        self._modules = load_modules_from_config()
        self._architectures = self._load_architectures(self._modules)

    @staticmethod
    def _load_architectures(modules) -> dict:
        '''
            Loads architecture constructors
        '''
        loaded_architectures = {} 
        for module in modules:
            architectures = getattr(module, ROTTNEST_ARCHITECTURE_MODULE_TAG, None)

            # Module has no architectures exposed
            if architectures is None:
                print(f"Module {module} does not contain any rottnest architectures")
                print(f'To expose an architecture at the module level, please set a "{ROTTNEST_ARCHITECTURE_MODULE_TAG}" variable in the module\'s main __init__.py')
                continue

            for architecture in architectures:
                try:
                    key = architecture.get_name()
                    loaded_architectures[key] = architecture
                except AttributeError:
                    print(f"Architecture {architecture} in module {module} does not implement the RottnestArchitecture interface")

        return loaded_architectures

    def __getitem__(self, key):
        '''
            Getter based on keys
            This is useful for hooking architecture selection with the front-end using a string based map
        '''
        return self._architectures.get(key, None)

    def set_current_architecture(self, key):
        '''
            Setter method for the current architecture
            Treats this class as the sole interface for passing architecture information to the front end
        '''
        arch = self[key]
        if arch is None:
            print(f"Unknown architecture {arch}")
        else:
            current_architecture = self[key] 

    def get_architecture_names(self):
        '''
           Retrieves a list of dtos of the architectures
           that the front-end can select from.

           Current it is thin but will be expanded
        '''
        return list(self._architectures.keys())
        
        #for k, v in self.:
        #    dtos.append(
        #             'arch_name': name,
        #     })
        #return dtos

    @staticmethod
    def load_plugin_map_from_file(plugin_name, filepath):
        '''
           Loads a python module from file 
           Calls `all_architectures()` and registers them
        '''
        spec = importlib.util.spec_from_file_location(plugin_name, filepath)
        plugin_obj = importlib.util.module_from_spec(spec)

        # NOTE: There should be better way instead of relying on sys here
        sys.modules[plugin_name] = plugin_obj
        spec.loader.exec_module(plugin_obj)

        return ArchPluginMap.retrieve_plugin_map(plugin_name, plugin_obj, plugin_name)


    @staticmethod
    def load_plugin_map_from_module(module_name):
        '''
           Loads a python module from module space
           Calls `all_architectures()` and registers them
        '''
        module = importlib.import_module(module_name)
        





class ArchPluginRegistry:
    '''
       Registry of architecture factories 
    '''
    def __init__(self):
        '''
           ArchPluginRegistry, holds a registry of architecture
           factories that can be constructed. 
        '''
        # TODO: Remove this later
        lat = ArchPluginMap.load_debug_lat2d()
        self.arch_map = {lat.identifier: lat}

    def register_plugin(self, name, plugin_map):
        '''
           Registers a plugin that can be constructed
        '''
        self.arch_map[name] = plugin_map

    def get_plugin(self, name):
        '''
           Retrieves a plugin  
        '''
        return self.arch_map[name]

    def to_config(self):
        '''
           We need to communicate the configuration
           over to the user, and allow it to be updated 
        '''
        arch_cfg = []
        for k, v in self.arch_map.items():
            ent = v.to_config_entry()
            arch_cfg.append(ent)
            
        return json.dumps(arch_cfg)

    def from_dict_interior_update(self, cfg):
        '''
            Attempts to update the current object
            based on a configuration object

            TODO: Implement this
        '''
        return False

    

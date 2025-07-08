

import sys
import importlib.util
import json
from rottnest.plugin.arch_location import ArchLocationKind

class ArchPluginMap:
    '''
       Architecture Plugin, holds an interface for
       operations  
    '''

    def __init__(self, identifier, plugin_map, location):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin  
        '''
        self.identifier = identifier
        self.api_map = {}
        #self.api_map = default_api_map(identifier)
        self.plugin_map = plugin_map
        self.location = location

    def get_plugin_map(self):
        '''
           Gets its own plugin map which is typically just
           1 architecture but many can be included so, it
           can handle many being attached and returned 
        '''
        self.plugin_map

    def to_config_entry(self):
        '''
           Moves the object into a config entry
           dictionary 
        '''
        return {
            "name": self.identifier,
            "location": self.location,
            "kind": ArchLocationKind.ModuleKey.to_name()
        }

    @staticmethod
    def load_debug_lat2d():
        '''
           Currently a debugging variant of the lat2d for trialing with
           built in plugin/archs 
        '''
        return ArchPluginMap('lat2d', {}, 'arch.lat2d')

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
    def load_plugin_map_from_module(plugin_name, location):
        '''
           Loads a python module from module space
           Calls `all_architectures()` and registers them
        '''
        plugin_obj = importlib.import_module(location)
        # It is not known what function to call
        
        return ArchPluginMap.retrieve_plugin_map(plugin_name, plugin_obj, location)

    @staticmethod
    def retrieve_plugin_map(name, modrep, location):
        '''
           Retrieves the architecture map object
           and extracts the list of plugins
        '''
        archmap = modrep.architectures()
        return ArchPluginMap(name, archmap.plugins(), location)

        


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

    def get_arch_dtos(self):
        '''
           Retrieves a list of dtos of the architectures
           that the front-end can select from.

           Current it is thin but will be expanded
        '''
        dtos = []
        for k, v in self.arch_map.items():
            dtos.append({
                             'arch_name': k,
                             "arch" : {
                                 'identifier': v.identifier,
                             }
                         })
        return dtos
    
    @staticmethod
    def from_plugin_map(plug_map):
        '''
           Constructs a plugin registry with a plugin map 
        '''
        reg = ArchPluginRegistry()
        for p in plug_map:
            reg.register_plugin(p)

        return reg


    @staticmethod
    def from_plugin_maps(plug_maps):
        '''
           Constructs a plugin registry with many plugin maps 
        '''
        reg = ArchPluginRegistry()
        for pm in plug_maps:
            for p in pm:
                reg.register_plugin(p)

        return reg
        

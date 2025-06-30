
import json
import importlib.util
from enum import Enum
from api_defaults import default_api_map

class ArchLocationKind(Enum):
    '''
       Location Kind, it outlines what kind of
       plugin it is and how that it is held within rottnest 
    '''
    FilePath = 1
    ModuleKey = 2


class ArchConfigEntry:
    '''
       Configuration entry that is used to describe the plugin
       The expectation is that it will be loaded as a json
       object
    '''
    def __init__(self, name, location, kind):
        '''
           Configuration entry, is a reference to where
           the config and arch kind it is. 
        '''
        self.name = name
        self.location = location
        self.kind = kind

    def get_name(self):
        '''
          Retrieves the name from ArchConfigEntry  
        '''
        return self.name

    def get_location(self):
        '''
           Gets the file path of the Architecture 
        '''
        return self.location

    def get_kind(self):
        '''
           Gets the kind of location data to load from
           - module_path: File
           - module_key: 
        '''
        return self.kind

    def load_arch(self):
        '''
           Loads an architecture that it is currently
           referring to. It will invoke 'load_arch'

           This will return an `ArchPlugin` object or None
        '''
        if self.kind == ArchLocationKind.FilePath:
            return ArchPluginMap.load_plugin_from_file(self.name, self.location)
        elif self.kind == ArchLocationKind.ModuleKey:
            return ArchPluginMap.load_plugin_from_module(self.name, self.location)
        else:
            None

        
class ArchRegistryConfig:
    '''
       Configuration for an arch registry
    '''
    def __init__(self, path, entries=[]):
        '''
           Constructs an arch configuration
           path is a filepath
           entries is a list
        '''
        self.path = path
        self.entries = entries
    
    @staticmethod
    def load_config(path):
        '''
          Loads a configuration file which will contain entries
          for the architecture to be used by the register
        '''
        entries = []
        with open(path, 'r') as file:
            contents = file.read()
            parsed_entries = json.loads(contents)
            for e in parsed_entries.items():
                name = e['identifier']
                description = e['description']
                kind = description['kind']
                location = description['location']

                entries.append(ArchConfigEntry(name, location, kind))
                
        config = ArchRegistryConfig(path, entries)
        return config    


class ArchPluginMap:
    '''
       Architecture Plugin, holds an interface for
       operations  
    '''

    def __init__(self, identifier, plugin_map):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin  
        '''
        self.identifier = identifier
        self.api_map = default_api_map(identifier)
        self.plugin_map = plugin_map
        

    @staticmethod
    def load_plugin_map_from_file(plugin_name, filepath):
        '''
           Loads a python module from file 
           Calls `all_architectures()` and registers them
        '''
        spec = importlib.util.spec_from_file_location(plugin_name, filepath)    
        plugin_obj = importlib.util.module_from_spec(spec)
        # It is not known what function to call
        
        
        return ArchPluginMap.retrieve_plugin_map(plugin_name, plugin_obj)


    @staticmethod
    def load_plugin_map_from_env(plugin_name, location):
        '''
           Loads a python module from module space
           Calls `all_architectures()` and registers them
        '''
        plugin_obj = importlib.import_module(location)
        # It is not known what function to call

        return ArchPluginMap.retrieve_plugin_map(plugin_name, plugin_obj)

    @staticmethod
    def retrieve_plugin_map(name, modrep):
        '''
           Retrieves the architecture map object
           and extracts the list of plugins
        '''
        archmap = modrep.architectures()
        return archmap.plugins()

        


class ArchPluginRegistry:
    '''
       Registry of architecture factories 
    '''
    def __init__(self):
        '''
           ArchPluginRegistry, holds a registry of architecture
           factories that can be constructed. 
        '''
        self.arch_map = {}

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
        

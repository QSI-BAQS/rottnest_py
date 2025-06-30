
import json
import importlib.util
from enum import Enum

class ArchLocationKind(Enum):
    FilePath = 1
    ModuleKey = 2


class ArchConfigEntry:

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
        '''
        if self.kind == ArchLocationKind.FilePath:
            with open(self.location, 'r') as cfg:

                contents = 
        elif self.kind == ArchLocatioNKind.ModuleKey:
            mod = importlib.
            
        else:
            None

        
class ArchConfig:

    def __init__(self, path):
        '''
           Constructs an arch configuration  
        '''
        self.path = path
        self.entries = {}
    
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
                location = e['identifier']

    


class ArchPlugin:
    '''
       Architecture Plugin, holds an interface for
       operations  
    '''

    def __init__(self, identifier):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin  
        '''
        self.identifier = identifier
        self.api_map = default_api_map(identifier)
        self.arch_map = {}
        

    @staticmethod
    def load_plugin_from_file(plugin_name, filepath):
        '''
           Loads a python module from file 
           Calls `all_architectures()` and registers them
        '''
        archplug = ArchPlugin(plugin_name)
        spec = importlib.util.spec_from_file_location(plugin_name, filepath)    
        plugin_obj = importlib.util.module_from_spec(spec)
        # It is not known what function to call
        
        
        return ArchPlugin.retrieve_plugin(plugin_obj)


    @staticmethod
    def load_plugin_from_env(plugin_name, location):
        '''
           Loads a python module from module space
           Calls `all_architectures()` and registers them
        '''
        archplug = ArchPlugin(plugin_name)
        plugin_obj = importlib.import_module(location)
        # It is not known what function to call

        return ArchPlugin.retrieve_plugin(plugin_obj)

    @staticmethod
    def retrieve_plugin(mod):
        return None

        


class ArchPluginRegistry:

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

    

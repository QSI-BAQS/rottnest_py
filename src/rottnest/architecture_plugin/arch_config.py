'''
    Architecture plugin management
    
    This is slightly convoluted only to allow for loading architectures from module names 
'''
import json
from .arch_plugin import ArchPluginMap, ArchPluginRegistry
from .arch_location import ArchLocationKind


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
        if ArchLocationKind.FilePath.equals(self.kind):
            return ArchPluginMap.load_plugin_map_from_file(self.name, self.location)
        elif ArchLocationKind.ModuleKey.equals(self.kind):
            return ArchPluginMap.load_plugin_map_from_module(self.name, self.location)
        else:
            return None


class ArchitectureRegistry:
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

    def load_arch_map(self, idx):
        '''
           Retrieves a particular arch map from an entry
        '''
        entry = self.entries[idx]
        return entry.load_arch()

    @staticmethod
    def load_config_or_default(path):
        '''
          Loads a configuration file which will contain entries
          for the architecture to be used by the register
        '''
        entries = []
        try:
            with open(path, 'r') as file:
                contents = file.read()
                parsed_entries = json.loads(contents)
                for entry in parsed_entries:
                    name = entry['identifier']
                    description = entry['description']
                    kind = description['kind']
                    location = description['location']

                    entries.append(ArchConfigEntry(name, location, kind))
        except Exception:
            print("Unable to load plugins, using defaults")
            path = None
            # TODO: Load in lat2d and dummyarch here
            
        config = ArchRegistryConfig(path, entries)
        return config    

    def to_plugin_registry(self):
        """
           Creates a plugin registry and consumes the config
           registry 
        """
        plgmaps = []
        for e in self.entries:
            plgmaps.append(e.load_arch())

        return ArchPluginRegistry.from_plugin_maps(plgmaps)

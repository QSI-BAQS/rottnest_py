import sys
import importlib.util
import json

from .plugin_manager import PluginManager

from ..architecture_interface.rottnest_architecture import ROTTNEST_ARCHITECTURE_MODULE_TAG

class ArchitecturePlugins(PluginManager):
    '''
       Architecture Plugin manager 
    '''

    def __init__(self, modules=None, config_path=None):
        '''
           Creates a new Plugin that can be used by
           rottnest, this plugin  
        '''

        if modules is None:
            modules = tuple()

        # Load from config
        super().__init__(
            module_tag = ROTTNEST_ARCHITECTURE_MODULE_TAG,
            modules = modules
        )
        self.architectures = self._load_architectures()
        if config_path is not None:
            self.load_config(config_path)

        self.current_architecture = None

    def load_config(self, filepath: str):
        '''
            Loads from a config file
        '''
        architectures = super().load_config(filepath)
        if architectures is FileNotFoundError:
            return FileNotFoundError
        self.architectures |= architectures
        return
       
    def load_architectures(self, *modules): 
        '''
            Setter method with public exposure
        '''
        self.architectures |= self._load_architectures(
            *modules
        )

    def _load_architectures(self, *modules) -> dict:
        '''
            Loads architecture constructors
            Default behaviour is that if the modules 
            argument is empty, then this defaults to
            the currently loaded modules in the superclass
        '''
        return self._load_objects(*modules)

    def __getitem__(self, key):
        '''
            Getter based on keys
            This is useful for hooking architecture 
            selection with the front-end using a 
            string based map
        '''
        return self.architectures.get(key, None)

    def set_current_architecture(self, key):
        '''
            Setter method for the current architecture
            Treats this class as the sole interface for 
            passing architecture information to the 
            front end
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
        '''
        return list(self._architectures.keys())
        
        #for k, v in self.:
        #    dtos.append(
        #             'arch_name': name,
        #     })
        #return dtos

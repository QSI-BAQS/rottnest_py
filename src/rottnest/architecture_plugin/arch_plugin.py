

from rottnest.compute_units.architecture_proxy import ArchitectureProxy

class ArchitecturePlugins(ArchitectureProxy):
    '''
        Uses the rottnest plugin base object as an assumption
        on what is imported
    '''
    def __init__(self, architecture_id, rottnest_plugin):
        '''
          Inherits from the proxy and also utilises the plugin
          map that is from the arch plugin loader  
        '''
        super().__init__(self, architecture_id)
        self.rottnest_plugin = rottnest_plugin

    def get_designer(self, arch_id):
        '''
           Gets the path to where the designer is for the frontend 
        '''
        return self.get_plugin_map()[arch_id].get_designer()


    def get_visualiser(self, arch_id):
        '''
            Gets the visualiser type 
        '''
        return self.get_plugin_map()[arch_id].get_visualiser()

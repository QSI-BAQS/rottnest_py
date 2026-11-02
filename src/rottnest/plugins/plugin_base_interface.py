'''
    Base class for extensible interface
'''

class RottnestPluginExtensibleInterface(abc.ABC):
    '''
        Extensible interface for rottnest plugin system
    '''
  
    @classmethod
    def get_name(cls): 
        raise NotImplementedError

    @classmethod
    def get_parameters(cls):
        raise NotImplementedError


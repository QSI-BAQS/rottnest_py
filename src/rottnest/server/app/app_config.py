from rottnest.executables.executable_map import ExecutableMap
from rottnest.executables.executable_state import ExecutableState
from rottnest.plugins.architecture_plugins import ArchitecturePlugins


ARCHITECTURE_REGISTRY_CFG = 'cfgs/architectures.json'
PROGRAM_REGISTRY_CFG = 'cfgs/programs.json'

class AppExtensions:
    '''
       Simple class that can be extended 
    '''
    def __init__(self):
        '''
           Initialises with no fields set 
        '''
        pass


class AppComponentLoader:
    '''
       AppComponentLoader allows for components to be attached
       to the application that will be invoked on initialisation 
    '''

    def __init__(self, path, attr_name, lfn):
        '''
           path is used in parting with
           the lambda function

           lambda function that is associated 
        '''

        self.path = path
        self.attr_name = attr_name
        self.lfn = lfn

    def load_component(self, target):
        '''
           Will load the component and attach
           it to the target object

           Will also create a getter method for said
           object
        '''

        ref_obj = self.lfn(self.path)

        def getter_fn():
            '''
               Getter for extended object 
            '''
            return getattr(target, self.attr_name)

        
        getter_name = 'get_{}'.format(self.attr_name)
        
        if ref_obj is not None:
            setattr(target, self.attr_name, ref_obj)
            setattr(target, getter_name, getter_fn)
        else:
            print("Returned Object was None, not setting attribute")
        

class ApplicationConfig:
    '''
       Application configuration object
       It holds configuration for the program map
       and architecture selector but will be extendable
       for other paths
    '''
    def __init__(self):
        '''
           Application Config constructor,
           will construct 
        '''

        self.entries = []

    def add_loader(self, loader):
        '''
           Adds a loader to the list 
        '''

        if isinstance(loader, AppComponentLoader):
            self.entries.append(loader)
        else:
            print("Unable to add loader")
        return self


    def load_and_attach(self, attach_target):
        '''
           Iterates through all entries and
            adds fields to a particular object
        '''
        for e in self.entries:
            e.load_component(attach_target)
            

    @staticmethod
    def default():
        '''
           Reasonable default static method to load programs
           and architectures that are core plugins 
        '''
        return ApplicationConfig().add_loader(
            AppComponentLoader(
                               PROGRAM_REGISTRY_CFG,
                               'exe_map',
                               lambda p : ExecutableMap
                               .from_config_or_default(p)
                           )
        ).add_loader(
            AppComponentLoader(
                               ARCHITECTURE_REGISTRY_CFG,
                               'arch_map',
                               lambda p : ArchitecturePlugins
                                .load_config_or_default()
                               
                           )
        ).add_loader(
            AppComponentLoader(
                               None,
                               'exe_state',
                               lambda _ : ExecutableState()
                           )
        )

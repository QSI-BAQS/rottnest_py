from rottnest.executables.executable_map import ExecutableMap
from rottnest.executables.executable_state import ExecutableState

class AppComponentLoader:

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

        def getter_fn(s):
            '''
               Getter for extended object 
            '''
            return getattr(s, self.attr_name)

        
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
                               'cfgs/programs.json',
                               'exe_map',
                               lambda p : ExecutableMap.from_config_or_default(p)
                           )
        ).add_loader(
            AppComponentLoader(
                               'cfgs/architectures.json',
                               'arch_map',
                               lambda p : print("Currently unimplemented")
                           )
            
        ).add_loader(
            AppComponentLoader(
                               None,
                               'exe_state',
                               lambda _ : ExecutableState()
                           )
        )

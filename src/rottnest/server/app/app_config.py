
import os
# from rottnest.debug.monitor import DebugMonitor

ARCHITECTURE_REGISTRY_CFG = 'architectures'
PROGRAM_REGISTRY_CFG = 'executables'
RESPONDER_REF = 'responder_ref'

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
        # else:
        #     DebugMonitor.with_obj('Unable to add loader', 'AppComponentConfig')
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
        from rottnest.server.responder import responder

        return ApplicationConfig().add_loader(
            AppComponentLoader(
                               PROGRAM_REGISTRY_CFG,
                               'exe_map',
                               exec_plugin_loader
                           )
        ).add_loader(
            AppComponentLoader(
                               ARCHITECTURE_REGISTRY_CFG,
                               'arch_map',
                               arch_plugin_loader
                               
                           )
        ).add_loader(
            AppComponentLoader(
                               RESPONDER_REF,
                               'responder_ref',
                               lambda p: responder
                               
                           )
        )

def exec_plugin_loader(pth: str):
    '''
       Loads the executable plugin, ensures that a
       current executable has been constructed 
    '''
    from rottnest.plugins import executables

    current_executable = None
    if len(executables) > 0: 
        current_executable = next(iter(executables)) 
 
    if current_executable is not None:
        executables.set_current_executable(current_executable)
    
    return executables 

def arch_plugin_loader(pth: str):
    '''
       Loads the plugins but also ensures the mapping
       for the api exist 
    '''
    from rottnest.server.responder import responder
    from rottnest.plugins import architectures

    for key, arch in architectures.get_architectures().items():
        desobj = arch.designer.get_designer_data()
        apimap = desobj['api']
        mask = apimap['mask']
        spec = apimap['spec']
        
        for sp in spec:
            sk, sr = sp
            fullname = f"{mask}.{sk}"
            sfn = sr
            responder.register_directly(fullname, sfn)
        
    return architectures

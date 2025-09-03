from rottnest.executables.executable_state import ExecutableState
from rottnest.plugins.executable_plugins import ExecutablePlugins
from rottnest.plugins.architecture_plugins import ArchitecturePlugins
from rottnest.server.responder import responder
# from rottnest.debug.monitor import DebugMonitor

ARCHITECTURE_REGISTRY_CFG = 'architectures'
PROGRAM_REGISTRY_CFG = 'executables'

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
        # else:
        #     DebugMonitor.with_obj('Unable to load component', 'AppComponentLoader')

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
                               None,
                               'exe_state',
                               lambda _ : ExecutableState()
                           )
        )

def exec_plugin_loader(pth: str):
    '''
       Loads the executable plugin, ensures that a
       current executable has been constructed 
    '''
    plugins = ExecutablePlugins.from_config_or_default(pth)
    current_exe = None
    

    for k, p in plugins.get_executables().items():
        if current_exe is None:
            current_exe = k

    if current_exe:
        plugins.set_current_executable(current_exe)
    
    return plugins

def arch_plugin_loader(pth: str):
    '''
       Loads the plugins but also ensures the mapping
       for the api exist 
    '''
    plugins = ArchitecturePlugins.load_config_or_default(pth)
    for k, p in plugins.get_architectures().items():
        desobj = p.designer.get_designer_data()
        apimap = desobj['api']
        # TODO: Finish this function
        mask = apimap['mask']
        spec = apimap['spec']

        
        for sp in spec:
            sk = sp[0]
            sr = sp[1]
            fullname = f"{mask}.{sk}"
            sfn = sr
            responder.register_directly(fullname, sfn)
        
    return plugins

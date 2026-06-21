'''
    Message kinds within this section are outlined under their own
    name space and are composed by the main `Rottnest`
    class 
'''
from types import FunctionType, MethodType, ClassMethodDescriptorType
import json

def _compose(cls, parent=None):
    '''
       Composing string via the type system symbols
       Making the deepest string prefixed with ancestor types 
    '''
    class_name = parent.__name__.lower() \
        if parent is not None else cls.__name__.lower()    
    for prop in cls.__dict__:
        if '__' not in prop:
            if type(cls.__dict__[prop]) is str:
                setattr(cls, prop, "{}.{}".format(class_name, cls.__dict__[prop]))
            elif type(cls.__dict__[prop]) not in \
                (FunctionType, MethodType, ClassMethodDescriptorType):
                setattr(cls, prop, _compose(cls.__dict__[prop],
                                            parent if parent is not None else cls))
            
    return cls


class Arch:
    '''
       Architecture related protocol messages 
    '''
    get_list = 'get_list'
    get_current = 'get_current'
    get_config = 'get_config'
    set_current_arch = 'set_current'
    set_config = 'set_config'
    save_config = 'save_config'
    load_config = 'load_config'

class Executable:
    '''
       Executable related protocol messages 
    '''
    get_list = 'get_list'
    get_current = 'get_current'
    get_config = 'get_config'
    set_current_arch = 'set_current'
    set_config = 'set_config'
    save_config = 'save_config'
    load_config = 'load_config'
    
class CallGraph:
    '''
       Callgraph related protocol messages 
    '''
    get_root_graph = 'get_root_graph'
    get_graph = 'get_graph'
    run_graph_node = 'run_graph_node'
    get_status = 'get_status'


class Data:
    '''
       Data related protocol messages 
    '''
    run_result = 'run_result'

class LayoutErr:
    '''
       LayoutError related protocol messages 
    '''
    executable_invalid = 'executable_invalid'
    architecture_invalid = 'architecture_invalid'

class Layout:
    '''
       Layout related protocol messages 
    '''
    set_layout = 'set_layout'
    run_layout = 'run_layout'
    poll_status = 'poll_status'
    err = LayoutErr

class Procedure:
    '''
       Procedure related protocol messages 
    '''
    run_immediate = 'run_immediate'
    run_defer = 'run_defer'
    get_state = 'get_state'
    list_all = 'list_all'

class Synchronise:
    '''
        Synchronise related messages        
    '''
    get_state = "get"
    set_state = "set"

class RottnestPacketBuilder:
    '''
       Allows for building/composing a packet to be sent 
    '''

    def __init__(self, message_kind: str):
        '''
           Initialiser, will provide the payload 
        '''
        self.message_kind = message_kind
        self.payload = dict()

    @staticmethod
    def message(message_kind: str):
        '''
           Make a message only version, no packet 
        '''
        return json.dumps({
                              'message': message_kind
                          })

    def put(self, key: str, value):
        '''
           Allows populating the dictionarym make sure the value
           is serialisable 
        '''
        self.payload[key] = value
        return self

    def set_payload(self, payload):
        '''
           Sets the payload directly 
        '''
        self.payload = payload
        return self


    def build(self):
        '''
           Builds the packet and serialises it 
        '''
        return json.dumps({
                              'message': self.message_kind,
                              'payload': self.payload
                          })


class Rottnest:
    '''
        Root - Rottnest namespace which includes all protocl messages
    '''
    err = 'err'
    liveness = 'live'
    arch = _compose(Arch)
    layout = _compose(Layout)
    executable = _compose(Executable)
    callgraph = _compose(CallGraph)
    data = _compose(Data)
    procedure = _compose(Procedure)
    synchronise = _compose(Synchronise)

    
    @classmethod
    def start_packet(cls, name: str):
        return RottnestPacketBuilder(name)

    @classmethod
    def make_message(cls, name: str):
        return RottnestPacketBuilder.message(name)

'''
   Single instance which these are encompassed under 
'''
Rottnest = _compose(Rottnest)


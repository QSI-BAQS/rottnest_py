'''
    Operations that the websocket supports that will be
    utilised within a websocket operations object
'''
class Operations:
    '''
       Categorises the operations group 
    '''
    @classmethod
    def to_list(cls):
        '''
           Gets a list of operations that can be iterated over
           Will convert the fields to a list 
        '''
        class_dict = cls.__dict__
        operations_list = []
        for prop in class_dict:
            if '__' not in prop:
                operations_list.append(prop)
        
        return operations_list

class Noop(Operations):
    '''
       No operations listed 
    '''

class Arch(Operations):
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

class Executable(Operations):
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
    
class CallGraph(Operations):
    '''
       Callgraph related protocol messages 
    '''
    get_root_graph = 'get_root_graph'
    get_graph = 'get_graph'
    run_graph_node = 'run_graph_node'
    get_status = 'get_status'


class Data(Operations):
    '''
       Data related protocol messages 
    '''
    run_result = 'run_result'


class Layout(Operations):
    '''
       Layout related protocol messages 
    '''
    set_layout = 'set_layout'
    run_layout = 'run_layout'
    poll_status = 'poll_status'

class Procedure(Operations):
    '''
       Procedure related protocol messages 
    '''
    run_immediate = 'run_immediate'
    run_defer = 'run_defer'
    get_state = 'get_state'
    list_all = 'list_all'


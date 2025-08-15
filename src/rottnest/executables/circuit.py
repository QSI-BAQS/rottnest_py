

import copy
import importlib
import sys
from enum import Enum
from functools import partial


class CircuitLocationKind(Enum):
    '''
       Location Kind, it outlines what kind of
       program it is and how that it is held within rottnest 
    '''
    FilePath = 1
    ModuleKey = 2

    def equals(self, a):
        '''
           Compares the two objects to see if they match 
        '''
        return self.name == a

class CircuitReturnObj:
    '''
       Wrapper on the return of the
       invocation fn
    '''

    def __init__(self, obj):
        '''
           Holder of the returned object
           Allows for null checking before
           usage. 
        '''
        self.obj = obj

    def get_obj(self):
        '''
           Simply returns the object
           This may be None 
        '''

    def is_none(self):
        '''
            Checks to see if the returned object
            is None
        '''
        return self.obj is None

    def is_some(self):
        '''
           Checks to see if the return object
           is not None 
        '''
        return self.obj is not None

    def get_obj_or(self, fn):
        '''
           It will retrieve the object or
           invoke a function
        '''
        if self.obj is None:
            return fn()
        else:
            return self.obj
            
    

class CircuitInstance:
    '''
        Produced from a circuit description,
        This will represent a circuit instance that
        can be used with an architecture

        This also results in an instance with a predictable
        interface
    '''

    def __init__(self, desc_name, invfn, args):
        '''
           Initialises the instance 
        '''
        self.desc_name = desc_name
        self.invfn = invfn
        self.args = args


    def invoke_and_consume(self):
        '''
           Invokes the instance
           and deletes the invfn and args to None
           - Note: Not sure if this is useful but I guess
                   it is something 
        '''
        ret = CircuitReturnObj(self.invoke())
        self.inkfn = None
        self.args = None
        return ret
        

    def invoke(self):
        '''
           Invokes the circuit 
           returns a CircuitReturnObj
        '''
        if self.invfn is None:
            print('Unable to invoke instance')
            return CircuitReturnObj(None)
        return CircuitReturnObj(self.invfn(self.args))

    def get_partial(self):
        '''
           Generates a partial based on the invoke_fn
           field and args associated supplied
        '''
        return partial(self.invfn, self.args)



        
class CircuitDescription:
    '''
        TODO: Add a params list
       Circuit description,
       has:
           name: str
           invoker: fn(args)
           fn_args: Dict
           fn_params: (Optional) List<string>, default: None
           
           Please make sure that args does not contain
           any self-referential objects
    '''

    def __init__(self, name, invoke_fn, fn_args, fn_params=None, module_key=None):
        '''
           Initialises and constructs a circuit description
           that can be used to construct an instance 
        '''
        self.name = name
        self.invoke_fn = invoke_fn
        self.fn_args = fn_args
        self.module_key = module_key
        if fn_params is None:
            self.fn_params = self.derive_params()
        else:
            self.fn_params = fn_params

    def to_dto(self):
        '''
           Serialisable DTO that can be used by
           a front-end 
        '''
        return {
            "name": self.name,
            "args": self.fn_args,
            "params": self.fn_params
        }
    
    def to_config_entry(self):
        '''
           Serialisable DTO that can be used by
           a front-end 
        '''
        return {
            "name": self.name,
            "args": self.fn_args,
            "invoke_fn": self.invoke_fn.__name__,
            "params": self.fn_params
        }

    def derive_params(self):
        '''
           Will simply derive the parameters names
           as numbers, provide fn_params if you want names
           specify a list of the name parameters
        '''
        params = []
        for i in range(len(self.args)):
            params.append('{}'.format(i))
        return params

    @staticmethod
    def create_circuit_from_dict(circ_obj):
        '''
           Creates a circuit from a dictionary 
        '''
        return CircuitDescription(circ_obj['name'],
                                  circ_obj['invoke_fn'],
                                  circ_obj['args'],
                                  circ_obj['params'])
        

    @staticmethod
    def create_circuit_from(circ_obj):
        '''
            Creates a circuit description from
            a configuration entry
        '''

        name = circ_obj['name']
        kind = circ_obj['kind']

        if CircuitLocationKind.FilePath.equals(kind):
            return CircuitDescription.create_circuit_from_file(name, circ_obj)
        elif CircuitLocationKind.ModuleKey.equals(kind):
            return CircuitDescription.create_circuit_from_module(name, circ_obj)
        else:
            return None
        
    
    @staticmethod
    def create_circuit_from_module(name, circ_obj):
        '''
           Constructs a new circuit from a module
           name 
        '''
        
        path = circ_obj['path']
        invfn = circ_obj['invoke_fn']
        args = circ_obj['args']
        program_obj = importlib.import_module(path)

        invoke_fn = program_obj[invfn]
        if invoke_fn is not None:
            return CircuitDescription(name, invoke_fn, args)
        else:
            return None

        
    @staticmethod
    def create_circuit_from_file(name, circ_obj):
        '''
           Constructs a new circuit from a file path 
        '''

        path = circ_obj['path']
        invfn = circ_obj['invoke_fn']
        args = circ_obj['args']
        
        spec = importlib.util.spec_from_file_location(name, path)
        program_obj = importlib.util.module_from_spec(spec)
        sys.modules[name] = program_obj

        obj = None
        try:
            spec.loader.exec_module(program_obj)
            invoke_fn = program_obj[invfn]
            if invoke_fn is not None:
                obj = CircuitDescription(name, invoke_fn, args)
            else:
                obj = None
        except Exception:
            print("Unable to construct the circuit upon loading module")

        return obj

    def create_instance(self, input_args=None):
        '''
           Generates a circuit instance
           Will cause a deep copy on the args 
        '''
        name = self.name
        invfn = self.invfni
        inv_args = input_args
        if input_args is None:
            inv_args = copy.deepcopy(self.args)
        inst = CircuitInstance(name, invfn, inv_args)
        return inst

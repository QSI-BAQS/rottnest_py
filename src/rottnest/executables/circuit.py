

import importlib
import sys
from enum import Enum
from rottnest.executables.executable import RottnestExecutable


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

    def __init__(self, desc_name, executable: RottnestExecutable, args):
        '''
           Initialises the instance 
        '''
        self.desc_name = desc_name
        self.executable = executable
        self.args = args

    def invoke(self):
        '''
           Invokes the circuit 
           returns a CircuitReturnObj
        '''
        if self.executable is None:
            print('Unable to invoke instance')
            return CircuitReturnObj(None)
        return CircuitReturnObj(self.invfn(self.args))




        
class CircuitDescription:
    '''
        CircuitDescription that is used to provide
        a basic description of the input circuit
    '''

    def __init__(self, executable, module_key=None):
        '''
           Initialises and constructs a circuit description
           that can be used to construct an instance 
        '''
        self.name = executable.__name__
        self.executable = executable
        self.module_key = module_key

    def to_dto(self):
        '''
           Serialisable DTO that can be used by
           a front-end 
        '''
        return {
            "name": self.name,
            "params": self.executable.get_parameters()
        }
    
    def to_config_entry(self):
        '''
           Serialisable DTO that can be used by
           a front-end 
        '''
        return {
            "name": self.name,
            "executable": self.executable,
            "params": self.executable.get_parameters()
        }


    @staticmethod
    def create_circuit_from_dict(circ_obj):
        '''
           Creates a circuit from a dictionary 
        '''
        return CircuitDescription(circ_obj['executable'])
        

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

        exe_name = circ_obj['executable']
        path = circ_obj['path']
        program_obj = importlib.import_module(path)

        executable = program_obj[exe_name]
        if executable is not None:
            return CircuitDescription(executable)
        else:
            return None

        
    @staticmethod
    def create_circuit_from_file(name, circ_obj):
        '''
           Constructs a new circuit from a file path 
        '''

        
        exe_name = circ_obj['executable']
        path = circ_obj['path']
        spec = importlib.util.spec_from_file_location(name, path)
        program_obj = importlib.util.module_from_spec(spec)
        sys.modules[name] = program_obj

        obj = None
        try:
            spec.loader.exec_module(program_obj)
            executable = program_obj[exe_name]
            if executable is not None:
                obj = CircuitDescription(executable)
            else:
                obj = None
        except Exception:
            print("Unable to construct the circuit upon loading module")

        return obj

    def create_instance(self, input_args):
        '''
           Generates a circuit instance
           Will cause a deep copy on the args 
        '''
        executable = self.executable
        inv_args = input_args
        inst = CircuitInstance(executable, inv_args)
        return inst

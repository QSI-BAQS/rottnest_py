
import copy

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


class CircuitDescription:
    '''
       Circuit description,
       has:
           name: str
           invoker: fn(args)
           args: Dict
           
           Please make sure that args does not contain
           any self-referential objects
    '''

    def __init__(self, name, invoke_fn, fn_args):
        '''
           Initialises and constructs a circuit description
           that can be used to construct an instance 
        '''
        self.name = name
        self.invoke_fn = invoke_fn
        self.fn_args = fn_args

    def create_instance(self):
        '''
           Generates a circuit instance
           Will cause a deep copy on the args 
        '''
        name = self.name
        invfn = self.invfn
        args = copy.deepcopy(self.args)
        inst = CircuitInstance(name, invfn, args)
        return inst

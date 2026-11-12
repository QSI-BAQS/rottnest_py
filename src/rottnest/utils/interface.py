'''
    Interface validation function
'''
from functools import partial, reduce

class InterfaceSpecificationError(Exception):
    '''
        Interface expects arguements by
    '''
    def __init__(self, fn, argcount, expected):
        super().__init__(
            f"""Specification of function {fn} expected {expected} arguments, received {argcount}"""
        )

    
class InterfaceArgnameError(Exception):
    '''
        Interface expects a missing argument by name 
    '''
    def __init__(self, fn, argname):
        '''
            Argname missing
        '''
        super().__init__(
            f"""Method {fn} is missing arguement {argname}"""
        )
       

class Interface:
    '''
        Interface base type
        Registers methods for subclass interface checks 
    '''
    # Collector pattern
    # Works over context of last class interface 
    _INTERFACES = {} 
    _COLLECTOR_ARGCOUNT = []
    _COLLECTOR_ARGNAME = []

    def __init__(
        self,
        base_cls: type
    ): 
        '''
            Constructor and context setting
            From parse order, the validate functions are
            invoked before __init__
        '''
        self.base_cls = base_cls
        self.collected_argcount = Interface._COLLECTOR_ARGCOUNT
        self.collected_argname = Interface._COLLECTOR_ARGNAME
        Interface._COLLECTOR_ARGCOUNT = []
        Interface._COLLECTOR_ARGNAME = []
        Interface._INTERFACES[base_cls] = self
    
    @classmethod
    def validate_argcount_decorator(cls, fn):
        '''
            Registers the class for argcount validation
        '''
        cls._COLLECTOR_ARGCOUNT.append(fn) 
        return fn

    def validate_argcount(self, base_fn, instance_fn):
        '''
            Performs the argcount validation
        '''
        expected = base_fn.__code__.co_argcount
        observed = instance_fn.__code__.co_argcount
        if expected != observed:
            raise InterfaceSpecificationError(instance_fn, observed, expected)

    @classmethod
    def validate_argname_decorator(cls, fn):
        '''
            Registers the function for subclass validation 
        '''
        cls._COLLECTOR_ARGNAME.append(fn) 
        return fn

    def validate_argname(self, base_fn, instance_fn):
        '''
            Performs the argname validation
            This is useful for kwargs matching
        '''
        # Expected names
        # First N terms of co_varnames are the arguments
        expected = base_fn.__code__.co_varnames[:base_fn.__code__.co_argcount]
        observed = set(
            instance_fn.__code__.co_varnames[:instance_fn.__code__.co_argcount]
        )
        for argname in expected:
            if argname not in observed:
                raise InterfaceArgnameError(instance_fn, argname)

    @classmethod
    def validate_interface_implementation(cls, implementation: type):
        '''
            Validates whether an object implements all its base interfaces
        '''
        # Expand all base classes 
        for base in recurse_bases(implementation): 
            
            # Check if the base class is registered as an interface
            interface = cls._INTERFACES.get(base, None)
            if interface is not None:
                # Validate the implementation against the interface 
                interface.validate(implementation)

    def validate(self, instance: type):
        '''
            Run type validation from the interface over 
            this object
        '''
        mapping_proxy = instance.__dict__
        validation_fns = [self.validate_argcount, self.validate_argname]
        collectors = [self.collected_argcount, self.collected_argname]  

        # Run validators against collected objects 
        for base_fns, validator in zip(collectors, validation_fns):
            for base_fn in base_fns:
                name = base_fn.__name__

                # Name will not be in the mapping proxy
                # if it's subclassed
                if name in mapping_proxy: 
                    derived_fn = mapping_proxy[name]
                    validator(base_fn, derived_fn)
 
def interface_argcount(fn: callable):
    '''
        Dispatch to the interface decorator 
    '''
    return Interface.validate_argcount_decorator(fn)

def interface_argname(fn: callable):
    '''
        Dispatch to the interface decorator
    '''
    return Interface.validate_argname_decorator(fn)

def recurse_bases(obj) -> tuple[type]:
    '''
        Recursively expand all bases for an object
        Effectively finds all parent classes
    '''

    bases = {obj} 
    horizon = {obj}
    invariant = len(bases)
    prev_invariant = float('inf')

    # Recurse until we stop expanding
    while invariant != prev_invariant: 

        new_horizon = reduce(
            lambda a, b: a | b,
            map( 
                set,
                (obj.__bases__ for obj in horizon)
            )
        )
        # Reset horizon and collect bases
        bases |= new_horizon 
        horizon = new_horizon

        # Update invariant
        prev_invariant = invariant
        invariant = len(bases)

    return bases

def interface(cls):
    '''
        Class decorator for an interface
    '''
    # The class constructor also performs registration
    Interface(cls)

    cls._prev_init = cls.__init_subclass__
    # Needs to bind a classmethod to dynamically collect 
    # the subclass
    cls.__init_subclass__ = classmethod(init_subclass_wrapper)
    return cls

def init_subclass_wrapper(cls, *args, **kwargs):
    '''
        Inject over init subclass
    '''
    # Uncommenting this triggers segfaults lol
    # Looks like a race condition on the binding
    #cls._prev_init(*args, **kwargs)
    Interface.validate_interface_implementation(cls)

def validate_function_argcount(
        fn: callable,
        argcount: int,
        varnames: tuple[str] = None
    ):
    '''
    '''
    n_vars = len(fn.__code__.co__varnames)
    if n_vars != argcount: 
        raise InterfaceSpecificationError(fn, n_vars, argcount)

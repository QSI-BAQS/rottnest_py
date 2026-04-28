'''
    Single Instantiation
    Base class for objects that should have a single 
    instantiation This differs from a singleton 
    pattern as this actively throws errors when an
    object's __init__ is called a second time
    
    Additional feature is that `block_instantiation` 
    may be called to pre-empt an initial __init__
    This will fail if the object has already been 
    instantiated
    Multiple blocks on the same object has no effect
'''

class MultipleInstantiationException(Exception):
    '''
        Multiple instantiations of a SingleInstantiation
        object exception
    '''
    _err = "Multiple instantiation of type {cls}"

    def __init__(self, cls=None, *, msg=None): 
        if msg is None:
            msg = self._err.format(cls=cls)
        super().__init__(msg)

class BlockingInstantiatedObjectException(Exception):
    '''
        Blocking an object that has already been
        instantiated
        Implies that an init call may be triggered
        before the block call
    '''

    _err = "Blocking instantiated object of type {cls}"

    def __init__(self, cls=None, *, msg=None): 
        if msg is None:
            msg = self._err.format(cls=cls)
        super().__init__(msg)

class InstantiatingBlockedObjectException(Exception):
    '''
        __init__ called on a blocked object.        
    '''

    _err = "Instantiating blocked object of type {cls}"

    def __init__(self, cls=None, *, msg=None): 
        if msg is None:
            msg = self._err.format(cls=cls)
        super().__init__(msg)

class SingleInstantiation:
    '''
        Not quite a singleton pattern
        This object should instantiate exactly once
        Additionally there's a `block` pattern
        that can be used to pre-emptively block 
        the instantiation of a class
    '''
    _singletons = dict() 
    BLOCKED = object()

    def __new__(cls, *args, **kwargs):
        '''
            Overloads new to test for blocked or 
            instantiated objects prior to an __init__
            call.
        '''

        obj = SingleInstantiation._singletons.get(cls, None) 
        # Blocking call made on this object
        if obj is SingleInstantiation.BLOCKED:
            raise InstantiatingBlockedObjectException(cls)

        # Object of this type already instantiated
        if obj is not None:
            raise MultipleInstantiationException(cls)

        obj = super().__new__(cls)
        cls._singletons[cls] = cls
        return obj

    @staticmethod
    def block_instantiation(cls: type):
        '''
            Blocks the instantiation of an object of type 
            cls
        '''
        obj = SingleInstantiation._singletons.get(cls, None)
        if obj is None:
            SingleInstantiation._singletons[cls] = SingleInstantiation.BLOCKED
            return
        if obj is not SingleInstantiation.BLOCKED:
            raise BlockingInstantiatedObjectException(cls)

        # Already blocked
        return

def block_instantiation(cls):
    '''
        Dispatch to SingleInstantiation.block_instantiation
    '''
    SingleInstantiation.block_instantiation(cls)

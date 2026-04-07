'''
    Synchronsied singleton instance of patchers
'''
from functools import reduce
from . import pyliqtr_patcher, qualtran_patcher, cirq_patcher

class PatchingSingleton: 
    '''
        This is a singleton instance used for scoping
    '''
    hash_function_patchers = {}
    patching_modules = [pyliqtr_patcher, qualtran_patcher, cirq_patcher]

    @classmethod
    def add_pyliqtr_hash(cls, patcher, function):
        pyliqtr_patcher.hash_function_patchers[patcher] = function

    @classmethod
    def add_qualtran_hash(cls, patcher, function):
        qualtran_patcher.hash_function_patchers[patcher] = function

    @classmethod
    def add_cirq_hash(cls, patcher, function):
        cirq_patcher.hash_function_patchers[patcher] = function

    @classmethod
    def load_hash_patcher(cls) -> dict:
        '''
            Triggers a reload of the hash patcher
            This is used to force updates on the 
            target objects
        '''
        for module in cls.patching_modules:
            module.monkey_patch()

        # Composition rather than assignment maintains the address
        # of the object
        cls.hash_function_patchers |= reduce(
            lambda x, y: x | y.hash_function_patchers,
            cls.patching_modules,
            dict() 
        )
        return cls.hash_function_patchers

    @classmethod
    def clear_hash_patcher(cls):
        '''
            Clears the current patchers
            This prevents loading by the parser
        '''
        cls.hash_function_patchers.clear()

    @classmethod
    def get_hash_patcher(cls) -> dict:
        return cls.hash_function_patchers

    @classmethod
    def get_tracking_targets(cls) -> set:
        '''
            Just the tracking target objects
        '''
        return set(cls.hash_function_patchers) 

# Singleton instance
patching_singleton = PatchingSingleton()

def add_pyliqtr_hash(patcher, function):
    '''
        Singleton dispatch method
        Adds a pyliqtr hash
    '''
    patching_singleton.add_pyliqtr_hash(patcher, function)

def add_qualtran_hash(patcher, function):
    '''
        Singleton dispatch method
        Adds a pyliqtr hash
    '''
    patching_singleton.add_qualtran_hash(patcher, function)

def add_cirq_hash(patcher, function):
    '''
        Singleton dispatch method
        Adds a cirq hash
    '''
    patching_singleton.add_cirq_hash(patcher, function)

def get_hash_patcher() -> dict:
    '''
        Singleton dispatch
    '''
    return patching_singleton.get_hash_patcher()

def load_hash_patcher() -> dict:
    '''
        Singleton dispatch
    '''
    return patching_singleton.load_hash_patcher()

def get_tracking_targets() -> set:
    '''
        Singleton dispatch
    '''
    return patching_singleton.get_tracking_targets()

def rottnest_hash(self):
    '''
        Dispatch method for rottnest hashing
    '''
    if self.gate.__class__ in hash_function_patchers:
        return self.gate._rottnest_hash(self)
    # Non-hashing object
    return None

def clear_hash_patcher():
    '''
        Singleton Dipatch
    '''
    patching_singleton.clear_hash_patcher()

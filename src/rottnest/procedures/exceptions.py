'''
    Compiler sequence exceptions
'''

class UnspecifiedDependencyError(Exception):
    '''
        Error thrown when a dependency is not 
         specified
        :: err : str :: Name of the dependency
    '''
    MSG = "Unspecified Dependency: {err}"
    def __init__(self, err):
        super().__init__(self.MSG.format(err=err))
        

class UnresolvableDependencyError(Exception):
    '''
        Error thrown when no stages have resolvable
          dependencies
    '''
    MSG = "Could not resolve any dependencies, possible circular or unspecified dependency"
    def __init__(self):
        super().__init__(self.MSG)


class DoubleExecutionError(Exception): 
    MSG = "Cannot double execute a compiler sequence"
    def __init__(self):
        super().__init__(self.MSG)


class DuplicateStageTagError(Exception):
    MSG = "Duplicate stage tag {tag}"
    def __init__(self, tag):
        super().__init__(self.MSG.format(tag=tag))


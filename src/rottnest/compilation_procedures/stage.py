'''
    Rottnest Compiler Stage
    Abstract base class for a compiler stage
'''
import abc

def stage_tag(stage: object):
    '''
        Helper method that maps stage objects to tags
    '''
    # In case a tag is passed in
    if isinstance(stage, str):
        return stage

    try:
        if isinstance(stage, type):
            # Check for a tag override
            if (tag := stage.TAG) is not None:
                return tag 

            # Use the class name
            return stage.__name__
       
        if (tag := stage.get_tag()) is not None: 
            return tag

        if (tag := stage.TAG) is not None:
            return tag 

        # Use the class name
        return stage.__class__.__name__

    except AttributeError:
        raise Exception(f"{stage} is not a tagged objedt")


class RottnestCompilerStage(abc.ABC):
    '''
        RottnestCompilerStage
        Interface for compiler stages
        Resolved by a RottnestCompilerPass
        :: tag : str :: 
        :: dependencies : list :: List of dependent tags
    '''

    TAG = None

    def __init__(
        self,
        *,
        tag: str = None,
        dependencies: list[str | type] = None,
        asynchronous: bool = False
    ): 
        '''
Constructor for a stage
:: tag : str :: Tag for this object 
  defaults to None, in which case it collects
  the name of the parent class
:: dependencies : list[str | type] :: Tags on which
  this stage depends 
:: asynchronous : bool :: Does this stage execute asynchronously
        '''
        
        # Default to whatever is passed in
        if tag is None:
            # Prevent a recursion
            self._tag = None 
            tag = stage_tag(self)
        self._tag = tag
    
        if dependencies is None:
            dependencies = list()
        self._dependencies = dependencies 
        self._complete = False

        self._asynchronous = asynchronous

    def get_tag(self) -> str:
        '''
            Getter for the stage tag
        '''
        return self._tag

    def get_dependencies(self) -> list:
        '''
            Getter for the dependencies
        '''
        return self._dependencies

    def is_asynchronous(self) -> bool:
        '''
            Getter for asynchronous tag
        '''
        return self._asynchronous

    def dependencies_resolved(
        self,
        compiler_environment: "RottnestCompilerPass"
    ) -> bool:
        '''
            Checks that the environment has resolved 
            all dependencies for this stage
        '''
        for dependency in self.get_dependencies(): 
            if not compiler_environment.resolved(
                dependency
                ):
                return False
        return True

    @abc.abstractclassmethod
    def execute(
        self,
        compiler_environment: "RottnestCompilerPass"
    ):
        '''
            Per-stage abstract execution method
            It may be assumed that resolved tags
            are in the environment namespace        
        '''
        ...

    def complete(self):
        '''
            Function to singal that the stage is complete
            This is used in particular for asynch methods
        '''
        return self._complete

    def poll(self):
        '''
            Function to perform or re-trigger some incremental work for the stage
        '''
        pass

    def is_asynchronous(self):
        '''
            Asynch getter
        '''
        return self._asynchronous


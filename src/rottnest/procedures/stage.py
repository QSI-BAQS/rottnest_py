'''
    Rottnest Compiler Stage
    Abstract base class for a compiler stage
'''
import abc
from typing import Protocol

class StageInterface(Protocol):
    
    TAG: str


    def get_tag(self):
        '''
            Retrieves the tag held by the stage_tag object
        '''
        ...

def stage_tag(stage: StageInterface):
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


class RottnestCompilerStage(abc.ABC, StageInterface):
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
        tag: str | None = None,
        dependencies: list[str | type] | None = None,
        co_dependencies: list[str | type] | None = None,
        asynchronous: bool = False
    ): 
        '''
        Constructor for a stage

        :: tag : str :: Tag for this object 
            defaults to None, in which case it collects
            the name of the parent class

        :: dependencies : list[str | type] :: Tags on which
            this stage depends 

        :: codependencies : list[str | type :: Tags which should be running 
            simultaneously to this stage. Co-dependencies may not be circular

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

        if co_dependencies is None:
            co_dependencies = list()


        self._dependencies = dependencies 
        self._co_dependencies = co_dependencies 

        self._complete: bool = False

        self._asynchronous = asynchronous

    def get_tag(self) -> str | None:
        '''
            Getter for the stage tag
        '''
        return self._tag

    def get_dependencies(self) -> list:
        '''
            Getter for the dependencies
        '''
        return self._dependencies

    def get_co_dependencies(self) -> list:
        '''
            Getter for the dependencies
        '''
        return self._co_dependencies

    def is_asynchronous(self) -> bool:
        '''
            Getter for asynchronous tag
        '''
        return self._asynchronous

    def is_codependent(self) -> bool:
        '''
            Getter for asynchronous tag
        '''
        return len(self._co_dependencies) > 0 


    def dependencies_resolved(
        self,
        compiler_environment: type["RottnestCompilerStage"] 
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

    def codependencies_resolved(
        self,
        compiler_environment: "RottnestCompilerStage"
    ):
        for co_dependency in self.get_co_dependencies():
            if not compiler_environment.current_asynchronous_stages(
                co_dependency 
            ): 
                return False
        return True


    def current_asynchronous_stages(self, tag): 
        '''
            As part of procedure requiring this method, itself calling inside
            the codependencies_resolved component should result in an error
            if not implemented
        '''
        return NotImplementedError 

    @classmethod
    @abc.abstractmethod
    def execute(
        self,
        compiler_environment: "RottnestCompilerStage"
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
        if self._complete:
            self.finalise() 
        return self._complete

    def finalise(self):
        '''
            Helper function called before complete returned
            This performs any last lingering tasks that need to be cleared
        '''
        pass

    def poll(self):
        '''
            Function to perform or re-trigger some incremental work for the stage
        '''
        pass

    # def is_asynchronous(self):
    #     '''
    #         Asynch getter
    #     '''
    #     return self._asynchronous


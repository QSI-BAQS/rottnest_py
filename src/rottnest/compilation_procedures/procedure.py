'''
    Interface for compiler procedures 
    Eventually these will be exposed to the front 
     end via some interface
'''
from .stage import RottnestCompilerStage, stage_tag
from . import exceptions

class RottnestCompilerProcedure(RottnestCompilerStage):
    '''
        Compiler pass manager
        Basically just does dependency resolution
        Interface may be overloaded such that 
        A procedure is also a stage 
    '''

    def __init__(
        self, 
        executable,
        stages: list['RottnestCompilerStage'],
        *,
        tag = None,
        dependencies: list[str | type] = None 
        ):
        
        self._stages = dict() 
        self._stages_complete = set() 

        for stage in stages:
            tag = stage.get_tag()
            if tag in self._stages:
                raise exceptions.DuplicateStageTagError(tag)
            self._stages[tag] = stage 

        valid_dependencies, err = self.validate_dependencies()
        if not valid_dependencies:
            raise exceptions.UnspecifiedDependencyError(err)

        super().__init__(
            tag=tag,
            dependencies=dependencies
        )

    def execute(self, reporting=True): 
        '''
            Executes the stages
            Raises an exception if the dependencies
            are not resolveable

            Naive quadratic method
            Can be improved with a priority queue 
        '''
        if len(self._stages_complete) > 0:
            raise exceptions.DoubleExecutionError() 

        unresolved = dict(self._stages) 

        while not self.complete():

            unresolved_nxt = dict(unresolved)
            resolved_on_pass = False

            for tag, stage in unresolved.items():

                if tag in self._stages_complete:
                    continue            

                if stage.dependencies_resolved(self): 
                    stage.execute(self)

                    # Inject completed stage into 
                    self.__setattr__(tag, stage)
                    self._stages_complete.add(tag)

                    resolved_on_pass = True
                    unresolved_nxt.pop(tag)

            if not resolved_on_pass: 
                # Nothing resolved, throw an error
                raise exceptions.UnresolvableDependencyError()
            unresolved = unresolved_nxt

    def complete(self) -> bool:
        '''
            Check if this pass is complete
        '''
        return len(self._stages_complete) == len(self._stages)

    def resolved(self, tag) -> bool:
        '''
            Check if a tag is resolved
        '''
        return tag in self._stages_complete

    def validate_dependencies(self) -> bool:
        '''
            Checks if all dependencies have a pattern that resolves them
        '''
        for tag, stage in self._stages.items():
            for dependency in stage.get_dependencies():
                if dependency not in self._stages:
                    return False, dependency
        return True, None

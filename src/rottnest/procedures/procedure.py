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
        dependencies: list[str | type] = None,
        co_dependencies: list[str | type] = None,
        asynchronous = False
        ):
        
        self._stages = dict() 
        self._stages_complete = set() 

        self._current_asynchronous_stages = dict() 
        self._current_codepenent_stages = dict() 

        for stage in stages:
            tag = stage.get_tag()
            if tag in self._stages:
                raise exceptions.DuplicateStageTagError(tag)
            self._stages[tag] = stage 

        # Check that dependencies are valid
        valid_dependencies, err = self.validate_dependencies()
        if not valid_dependencies:
            raise exceptions.UnspecifiedDependencyError(err)
   
        # Check if asynchronous execution is needed 
        asynchronous = asynchronous or any(
            map(
                lambda x: x.is_asynchronous(),
                stages
            )
        )

        super().__init__(
            tag=tag,
            dependencies=dependencies,
            co_dependencies=co_dependencies,
            asynchronous = asynchronous
        )

    def execute(
            self,
            compiler_environment = None,
            reporting=True,
            single_pass=False
        ) -> bool: 
        '''
            Executes the stages
            Raises an exception if the dependencies
            are not resolveable

            Naive quadratic method
            Can be improved with a priority queue 
            Returns if execution has completed
        '''
        if self.complete():
            # Catches asynch completion of all stages 
            # Single pass is set by the asynch handler
            if single_pass:
                return True

            # Non-Asynch call triggers an exception
            raise exceptions.DoubleExecutionError() 

        # Iterate over unresolved stages
        # Also skip stages that are running asynchronously
        unresolved = {
            tag: stage 
            for tag, stage in self._stages.items()
            if tag not in self._stages_complete 
                and tag not in self._current_asynchronous_stages
        }

        while not self.complete():

            unresolved_nxt = dict(unresolved)
            resolved_on_pass = False

            for tag, stage in unresolved.items():

                # Tag is already complete
                # This may occur on an asynchronous stage  
                if tag in self._stages_complete:
                    continue            

                if (
                    stage.dependencies_resolved(self) 
                    and stage.codependencies_resolved(self)
                    ):
                    print("Executing: ", stage)
                    stage.execute(self)
                  
                    if stage.is_codependent():
                        self._current_codependent_stages[tag] = stage
 
                    if stage.is_asynchronous():
                        # Start and register asynch stage
                        self._current_asynchronous_stages[tag] = stage
                        self.__setattr__(tag, stage)
                        continue
 
                    # Inject completed stage into namespace
                    self.__setattr__(tag, stage)
                    self._stages_complete.add(tag)

                    resolved_on_pass = True
                    unresolved_nxt.pop(tag)

            # Don't run to completion
            if single_pass:
            
                # Check that we are not in an invalid state
                if (
                    len(self._current_asynchronous_stages) == 0
                and not resolved_on_pass
                and not self.complete()):
                    raise exceptions.UnresolvableDependencyError()

                # Single pass completed, break
                break

            if not resolved_on_pass: 
                # Nothing resolved, throw an error
                raise exceptions.UnresolvableDependencyError()
            unresolved = unresolved_nxt

            return self.complete() 
            

    def poll(self, environment = None):
        '''
            Polling function during asynchronous execution
        '''
        dequeue = []
        for tag, stage in self._current_asynchronous_stages.items():
            if stage.complete():
                print("COMPLETE: ", stage)
                dequeue.append(stage)
            else: 
                print(f"Polling: {stage.get_tag()}")
                stage.poll(self)
                if stage.complete():
                    dequeue.append(stage)

        for stage in dequeue: 
            self._current_asynchronous_stages.pop(tag)
            self._stages_complete.add(stage.get_tag())

        self.execute(single_pass=True)

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

    def current_asynchronous_stages(self, tag): 
        '''
            Check if a tag is currently executing asynchronously
        '''
        return tag in self._current_asynchronous_stages 

    def validate_dependencies(self) -> bool:
        '''
            Checks if all dependencies have a pattern that resolves them
        '''
        for tag, stage in self._stages.items():
            for dependency in stage.get_dependencies():
                if dependency not in self._stages:
                    return False, dependency
        return True, None

import unittest

from rottnest.compilation_procedures import procedure, stage, exceptions

class CompilerStageTest(unittest.TestCase):

    def get_stage_class(self, *, fn=None): 


        def execute(self, obj):
            ...

        if fn is None:
            fn = execute

        class Stage(stage.RottnestCompilerStage):
            def __init__(self, tag=None, dependencies=None):
                super().__init__(
                    tag=tag,
                    dependencies=dependencies
                )

            def execute(self, obj):
                # Instantiated to make non-abstract
                ...
 
        Stage.execute = fn

        return Stage

    def test_no_dependencies(self):

        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [stage_class(tag="one")]
                super().__init__(None, stages) 

        env = Environment()
        env.execute()
        assert env.one

    def test_one_dependency(self):

        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [
                    stage_class(tag="one"),
                    stage_class(tag="two", dependencies=["one"])
                 ]
                super().__init__(None, stages) 

        env = Environment()
        env.execute()
        assert env.complete()
        assert env.one
        assert env.two

    def test_two_dependencies(self):

        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [
                    stage_class(tag="one"),
                    stage_class(tag="two", dependencies=["one"]),
                    stage_class(tag="three", dependencies=["two"])

                 ]
                super().__init__(None, stages) 

        env = Environment()
        env.execute()
        assert env.one
        assert env.two
        assert env.three

    def test_unspecified_dependency(self):
        '''
            Tests a dependency with no resolution tag
        '''
        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [
                    stage_class(tag="one"),
                    stage_class(tag="two", dependencies=["seven"]),

                 ]
                super().__init__(None, stages) 

        caught = False 
        try:
            env = Environment()
        except exceptions.UnspecifiedDependencyError: 
            caught = True
        assert caught

    def test_duplicate_tag(self):
        '''
            Tests a dependency with no resolution tag
        '''
        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [
                    stage_class(tag="one"),
                    stage_class(tag="one"),

                 ]
                super().__init__(None, stages) 

        caught = False 
        try:
            env = Environment()
        except exceptions.DuplicateStageTagError: 
            caught = True
        assert caught

    def test_circular_dependency(self):
        '''
            Tests a circular dependency 
        '''
        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [
                    stage_class(tag="one", dependencies=['two']),
                    stage_class(tag="two", dependencies=["one"]),

                 ]
                super().__init__(None, stages) 


        env = Environment()

        caught = False 
        try:
            env.execute()
        except exceptions.UnresolvableDependencyError: 
            caught = True
        assert caught


    def test_double_execution(self):
        '''
            Tests executing twice 
        '''
        stage = self.get_stage_class()

        class Environment(procedure.RottnestCompilerProcedure): 
            def __init__(self):
                stage_class = stage
                stages = [
                    stage_class(tag="one"),
                    stage_class(tag="two", dependencies=["one"]),

                 ]
                super().__init__(None, stages) 

        env = Environment()

        caught = False 
        env.execute()

        try:
            env.execute()
        except exceptions.DoubleExecutionError: 
            caught = True
        assert caught



if __name__ == '__main__':
    tst = CompilerStageTest()
    tst.test_no_dependencies()

    #unittest.main()
